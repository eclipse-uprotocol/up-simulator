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

import os
import pickle
import signal
import time
from pathlib import Path
from sys import platform, exit
from threading import current_thread, main_thread

from google.protobuf import text_format, any_pb2
from uprotocol.proto.uattributes_pb2 import UPriority
from uprotocol.proto.umessage_pb2 import UMessage
from uprotocol.proto.upayload_pb2 import UPayload
from uprotocol.proto.upayload_pb2 import UPayloadFormat
from uprotocol.proto.uri_pb2 import UEntity, UUri
from uprotocol.rpc.rpcmapper import RpcMapper
from uprotocol.transport.builder.uattributesbuilder import UAttributesBuilder
from uprotocol.uri.factory.uresource_builder import UResourceBuilder
from uprotocol.uri.serializer.longuriserializer import LongUriSerializer

from simulator.core import protobuf_autoloader
from simulator.core.exceptions import SimulationError
from simulator.core.transport_layer import TransportLayer
from simulator.utils import common_util

RESPONSE_URI = UUri(entity=UEntity(name="simulator", version_major=1), resource=UResourceBuilder.for_rpc_response())

covesa_services = []


def get_instance(entity):
    for entity_dict in covesa_services:
        if entity_dict.get('name') == entity:
            return entity_dict.get('entity')


class BaseService(object):
    # instance = None

    def __init__(self, service_name=None, portal_callback=None, use_signal_handler=True):

        self.service = service_name
        self.subscriptions = {}
        self.portal_callback = portal_callback
        self.transport_layer = TransportLayer()
        self.publish_data = []
        self.state = {}  # default variable to keep track of the mock service's state
        self.state_dir = os.path.join(str(Path.home()), ".sdv")  # location of serialized state
        self.state_file = os.path.join(self.state_dir, str(self.__class__.__name__))

        if use_signal_handler and (current_thread() is main_thread()):
            # register signal handler to quit
            signal.signal(signal.SIGINT, self.signal_handler)
            if platform == "linux" or platform == "linux2":
                signal.signal(signal.SIGTSTP, self.signal_handler)
            else:
                signal.signal(signal.SIGTERM, self.signal_handler)

        self.load_state()

    def RequestListener(func):
        class wrapper:
            @staticmethod
            def on_receive(message: UMessage):
                global instance
                print('wrapper on receive')
                attributes = message.attributes
                topic = attributes.sink
                entity = topic.entity.name
                method = topic.resource.instance
                payload = message.payload
                req = protobuf_autoloader.get_request_class(entity, method)
                res = protobuf_autoloader.get_response_class(entity, method)()
                any_message = any_pb2.Any()
                any_message.ParseFromString(payload.value)
                req = RpcMapper.unpack_payload(any_message, req)
                response = func(get_instance(entity), req, res)
                any_obj = any_pb2.Any()
                any_obj.Pack(response)
                payload_res = UPayload(value=any_obj.SerializeToString(), format=payload.format)
                attributes = UAttributesBuilder.response(RESPONSE_URI, attributes.sink, attributes.priority,
                                                         attributes.id).build()
                if get_instance(entity).portal_callback is not None:
                    get_instance(entity).portal_callback(req, method, response, get_instance(entity).publish_data)
                return TransportLayer().send(UMessage(attributes=attributes, payload=payload_res))

        return wrapper

    def start_rpc_service(self):
        if self.transport_layer.start_service(self.service):
            time.sleep(1)
            covesa_services.append({'name': self.service, 'entity': self})
            # create topic
            topics = protobuf_autoloader.get_topics_by_proto_service_name(self.service)
            # for topic in topics:
            if len(topics) >= 0:
                self.transport_layer.create_topic(self.service, topics, common_util.print_create_topic_status_handler)
            for attr in dir(self):
                if callable(getattr(self, attr)) and isinstance(getattr(self, attr), type):
                    for attr1 in dir(getattr(self, attr)):
                        if attr1 == 'on_receive':
                            func = getattr(self, attr)
                            method_uri = protobuf_autoloader.get_rpc_uri_by_name(self.service, attr)
                            status = self.transport_layer.register_rpc_listener(
                                LongUriSerializer().deserialize(method_uri), func)
                            common_util.print_register_rpc_status(method_uri, status.code, status.message)

                            break

    def publish(self, uri, params={}, is_from_rpc=False):

        message_class = protobuf_autoloader.get_request_class_from_topic_uri(uri)
        message = protobuf_autoloader.populate_message(self.service, message_class, params)
        any_obj = any_pb2.Any()
        any_obj.Pack(message)
        payload_data = any_obj.SerializeToString()
        payload = UPayload(value=payload_data, format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF)
        attributes = UAttributesBuilder.publish(LongUriSerializer().deserialize(uri), UPriority.UPRIORITY_CS4).build()
        status = self.transport_layer.send(UMessage(payload=payload, attributes=attributes))
        common_util.print_publish_status(uri, status.code, status.message)
        if is_from_rpc:
            self.publish_data.clear()
            self.publish_data.append(message)
        time.sleep(0.25)
        return message, status

    def subscribe(self, uris, listener):

        for uri in uris:
            if uri in self.subscriptions.keys() and listener == self.subscriptions[uri]:
                print(f"Warning: there already exists an object subscribed to {uri}")
                print(f"Skipping subscription for {uri}")
            self.subscriptions[uri] = listener
            status = self.transport_layer.register_listener(LongUriSerializer().deserialize(uri), listener)
            common_util.print_subscribe_status(uri, status.code, status.message)
            time.sleep(1)

    def start(self):

        if self.service is None:
            print("Unable to start mock service without specifying the service name.")
            print("You must set the service name in the BaseService constructor")
            raise SimulationError("service_name not specified for mock service")
        print("Waiting for events...")
        self.start_rpc_service()

        return self

    def disconnect(self):
        # todo write logic to unregister the rpc listener
        time.sleep(2)

    def print(self, protobuf_obj):

        print(f"Message: {protobuf_obj.DESCRIPTOR.full_name}")
        print(text_format.MessageToString(protobuf_obj))

    def signal_handler(self, sig, frame):

        print("Exiting gracefully....")
        exit()

    def init_message_state(self, message_class):
        state = {}
        message_fields = protobuf_autoloader.get_message_fields(message_class)
        default_obj = message_class()
        for field in message_fields:
            state[field] = getattr(default_obj, field)
        return state

    def save_state(self):
        try:
            if not os.path.exists(self.state_dir):
                os.makedirs(self.state_dir)

            print("Saving previous state...")
            with open(self.state_file, "wb+") as fd:
                pickle.dump(self.state, fd)
            print("Done!")
        except OSError as e:
            print("Unable to save state.")

    def load_state(self):
        try:
            print("Loading previous state...")
            with open(self.state_file, "rb") as f:  # "rb" because we want to read in binary mode
                self.state = pickle.load(f)
            print("Done!")
        except OSError as e:
            print("Unable to load previous state.")
