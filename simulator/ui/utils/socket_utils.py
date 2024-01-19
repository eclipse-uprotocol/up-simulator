# -------------------------------------------------------------------------
#
# Copyright (c) 2023 General Motors GTO LLC
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
# SPDX-FileType: SOURCE
# SPDX-FileCopyrightText: 2023 General Motors GTO LLC
# SPDX-License-Identifier: Apache-2.0
#
# -------------------------------------------------------------------------

import json
import logging
import os
import threading
import time
import traceback

from flask_socketio import SocketIO
from google.protobuf import any_pb2
from google.protobuf.json_format import MessageToDict
from uprotocol.proto.uattributes_pb2 import UAttributes
from uprotocol.proto.uattributes_pb2 import UPriority
from uprotocol.proto.upayload_pb2 import UPayload
from uprotocol.proto.upayload_pb2 import UPayloadFormat
from uprotocol.proto.uri_pb2 import UUri
from uprotocol.rpc.calloptions import CallOptions
from uprotocol.rpc.rpcmapper import RpcMapper
from uprotocol.transport.builder.uattributesbuilder import UAttributesBuilder
from uprotocol.transport.ulistener import UListener
from uprotocol.uri.serializer.longuriserializer import LongUriSerializer

import simulator.ui.utils.common_handlers as Handlers
import simulator.utils.constant as CONSTANTS
from simulator.core import transport_layer, protobuf_autoloader
from simulator.utils.common_util import verify_all_checks

logger = logging.getLogger('Simulator')


def start_service(entity, callback):
    if entity == "body.cabin_climate":
        from simulator.mockservices.cabin_climate import CabinClimateService
        CabinClimateService(callback).start()

    elif entity == "chassis.braking":
        from simulator.mockservices.braking import BrakingService
        BrakingService(callback).start()
    elif entity == "example.hello_world":
        from simulator.mockservices.hello_world import HelloWorldService
        HelloWorldService(callback).start()


class SocketUtility:

    def __init__(self, socket_io, req, transport_layer):
        self.socketio = socket_io
        self.oldtopic = ''
        self.vin = None
        self.last_published_data = None
        self.request = req
        self.sender = None
        self.transport_layer = transport_layer
        self.retry_rpc = 0
        self.retry_pub = 0
        self.retry_sub = 0
        self.lock_pubsub = threading.Lock()
        self.lock_rpc = threading.Lock()

    @staticmethod
    def entity_name_file(entity, filename):
        if os.path.isfile(filename):
            with open(filename, 'r+') as f:
                lines = f.read()
                f.seek(0)
                f.truncate()
                if len(lines) > 0:
                    services = json.loads(lines)
                else:
                    services = []
                services.append(entity)
                f.write(json.dumps(services, indent=2))
        else:
            services = []
            services.append(entity)
            try:
                with open(filename, 'a+') as fp:
                    fp.write(json.dumps(services, indent=2))

            except IOError as exc:
                pass

    def execute_send_rpc(self, json_sendrpc):
        try:
            status = verify_all_checks()
            if status == '':
                methodname = json_sendrpc['methodname']
                serviceclass = json_sendrpc['serviceclass']
                mask = json.loads(json_sendrpc["mask"])
                data = json_sendrpc['data']
                json_data = json.loads(data)

                req_cls = protobuf_autoloader.get_request_class(serviceclass, methodname)
                res_cls = protobuf_autoloader.get_response_class(serviceclass, methodname)

                if bool(mask):
                    json_data["update_mask"] = {'paths': mask}

                message = protobuf_autoloader.populate_message(serviceclass, req_cls, json_data)
                version = 1

                method_uri = protobuf_autoloader.get_rpc_uri_by_name(serviceclass, methodname, version)
                any_obj = any_pb2.Any()
                any_obj.Pack(message)
                payload_data = any_obj.SerializeToString()
                payload = UPayload(value=payload_data, format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF)
                method_uri = LongUriSerializer().deserialize(method_uri)
                attributes = UAttributesBuilder.request(UPriority.UPRIORITY_CS4, method_uri,
                                                        CallOptions.TIMEOUT_DEFAULT).build()

                res_future = self.transport_layer.invoke_method(method_uri, payload, attributes)
                sent_data = MessageToDict(message)

                message = "Successfully send rpc request for " + methodname
                if transport_layer.utransport == "Zenoh":
                    message = "Successfully send rpc request for " + methodname + " to Zenoh"
                res = {'msg': message, 'data': sent_data}
                self.socketio.emit(CONSTANTS.CALLBACK_SENDRPC, res, namespace=CONSTANTS.NAMESPACE)
                response = RpcMapper.map_response(res_future, res_cls)
                Handlers.rpc_response_handler(self.socketio, response.result())
            else:
                self.socketio.emit(CONSTANTS.CALLBACK_GENERIC_ERROR, status, namespace=CONSTANTS.NAMESPACE)

        except Exception:
            log = traceback.format_exc()
            self.socketio.emit(CONSTANTS.CALLBACK_SENDRPC_EXC, log, namespace=CONSTANTS.NAMESPACE)

    def execute_publish(self, json_publish):
        try:
            status = verify_all_checks()
            if status == '':
                topic = json_publish['topic']
                data = json_publish['data']
                service_class = json_publish['service_class']

                json_data = json.loads(data)

                req_cls = protobuf_autoloader.get_request_class_from_topic_uri(topic)

                message = protobuf_autoloader.populate_message(service_class, req_cls, json_data)

                self.last_published_data = MessageToDict(message, preserving_proto_field_name=True,
                                                         including_default_value_fields=True)
                new_topic = LongUriSerializer().deserialize(topic)
                any_obj = any_pb2.Any()
                any_obj.Pack(message)
                payload_data = any_obj.SerializeToString()
                payload = UPayload(value=payload_data, format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF)

                attributes = UAttributesBuilder.publish(UPriority.UPRIORITY_CS4).build()
                status = self.transport_layer.send(new_topic, payload, attributes)
                Handlers.publish_status_handler(self.socketio, self.lock_pubsub, self.transport_layer.utransport, topic,
                                                status.code, status.message, self.last_published_data)

                published_data = MessageToDict(message)
                self.socketio.emit(CONSTANTS.CALLBACK_PUBLISH_STATUS_SUCCESS,
                                   {'msg': "Publish Data  ", 'data': published_data}, namespace=CONSTANTS.NAMESPACE)

            else:
                self.socketio.emit(CONSTANTS.CALLBACK_GENERIC_ERROR, status, namespace=CONSTANTS.NAMESPACE)

        except:
            log = traceback.format_exc()
            self.socketio.emit(CONSTANTS.CALLBACK_EXCEPTION_PUBLISH, log, namespace=CONSTANTS.NAMESPACE)

    def start_mock_service(self, json_service):
        def handler(rpc_request, method_name, json_data, rpcdata):
            Handlers.rpc_logger_handler(self.socketio, self.lock_rpc, rpc_request, method_name, json_data, rpcdata)

        try:
            start_service(json_service['entity'], handler)
            time.sleep(1)
            self.entity_name_file(json_service['entity'], CONSTANTS.FILENAME_SERVICE_RUNNING_STATUS)
            self.socketio.emit(CONSTANTS.CALLBACK_START_SERVICE, json_service['entity'], namespace=CONSTANTS.NAMESPACE)
        except Exception as ex:
            logger.error(f'Exception:', exc_info=ex)

    def execute_subscribe(self, json_subscribe):
        topic = json_subscribe['topic']
        try:

            status = verify_all_checks()
            if status == '':
                # self.bus_obj_subscribe = BusManager(url=self.proxy_url, proxy_enable=self.is_proxy_enable,
                # vin=self.vin)
                # if self.oldtopic != '':
                #     self.bus_obj_subscribe.unsubscribe(self.oldtopic, self.common_unsubscribe_status_handler)
                new_topic = LongUriSerializer().deserialize(topic)
                status = self.transport_layer.register_listener(new_topic, SubscribeUListener(self.socketio,
                                                                                              self.transport_layer.utransport,
                                                                                              self.lock_pubsub))
                if status is None:
                    Handlers.subscribe_status_handler(self.socketio, self.lock_pubsub, self.transport_layer.utransport,
                                                      topic, 0, "Ok")
                else:
                    Handlers.subscribe_status_handler(self.socketio, self.lock_pubsub, self.transport_layer.utransport,
                                                      topic, status.code, status.message)

            else:
                self.socketio.emit(CONSTANTS.CALLBACK_GENERIC_ERROR, status, namespace=CONSTANTS.NAMESPACE)

        except Exception as ex:
            log = traceback.format_exc()
            self.socketio.emit(CONSTANTS.CALLBACK_EXCEPTION_SUBSCRIBE, log, namespace=CONSTANTS.NAMESPACE)


class SubscribeUListener(UListener):

    def __init__(self, socketio: SocketIO, utransport: str, lock_pubsub: threading.Lock):
        self.socketio = socketio
        self.utransport = utransport
        self.lock_pubsub = lock_pubsub

    def on_receive(self, topic: UUri, payload: UPayload, attributes: UAttributes):
        print("onreceive")
        Handlers.on_receive_event_handler(self.socketio, self.lock_pubsub, self.utransport,
                                          LongUriSerializer().serialize(topic), payload)
