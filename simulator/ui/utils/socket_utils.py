"""
SPDX-FileCopyrightText: Copyright (c) 2024 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
SPDX-FileType: SOURCE
SPDX-License-Identifier: Apache-2.0
"""

import json
import logging
import threading
import traceback

from flask_socketio import SocketIO
from google.protobuf import any_pb2
from google.protobuf.json_format import MessageToDict
from uprotocol.communication.calloptions import CallOptions
from uprotocol.communication.rpcmapper import RpcMapper
from uprotocol.communication.upayload import UPayload
from uprotocol.transport.ulistener import UListener
from uprotocol.uri.serializer.uriserializer import UriSerializer
from uprotocol.v1.uattributes_pb2 import UPayloadFormat
from uprotocol.v1.umessage_pb2 import UMessage

from simulator.ui.utils import common_handlers
from simulator.utils import constant
from simulator.utils.common_util import verify_all_checks
from simulator.utils.vehicle_service_utils import (
    get_service_instance_from_entity,
    start_service,
)
from tdk.apis.apis import TdkApis
from tdk.core import protobuf_autoloader
from tdk.helper import someip_helper
from tdk.helper.someip_helper import configure_someip_service, ensure_defaults
from tdk.helper.transport_configuration import TransportConfiguration

logger = logging.getLogger("Simulator")


class SocketUtility:
    def __init__(self, socket_io, transport_config: TransportConfiguration, tdk_apis: TdkApis):
        self.socketio = socket_io
        self.oldtopic = ""
        self.last_published_data = None
        self.transport_config = transport_config
        self.tdk_apis = tdk_apis
        self.lock_pubsub = threading.Lock()
        self.lock_rpc = threading.Lock()
        self.lock_pubsub = threading.Lock()
        self.lock_service = threading.Lock()

    async def execute_send_rpc(self, json_sendrpc):
        try:
            status = verify_all_checks(self.transport_config.get_transport_env())
            if status == "":
                methodname = json_sendrpc["methodname"]
                service_name = json_sendrpc["serviceclass"]
                mask = json.loads(json_sendrpc["mask"])
                data = json_sendrpc["data"]
                json_data = json.loads(data)
                service_id = protobuf_autoloader.get_entity_id_from_entity_name(service_name)
                req_cls = protobuf_autoloader.get_request_class(service_id, methodname)
                res_cls = protobuf_autoloader.get_response_class(service_id, methodname)

                if bool(mask):
                    json_data["update_mask"] = {"paths": mask}

                message = protobuf_autoloader.populate_message(service_name, req_cls, json_data)
                version = 1

                method_uri = protobuf_autoloader.get_rpc_uri_by_name(service_id, methodname, version)
                if someip_helper.is_serializer_enabled:
                    message = ensure_defaults(message)
                    payload_data = UPayload.serialize_someip(message)  # Use SOME/IP serialization
                    print(f"message after ensure defaults(SOMEIP) {message}")
                    payload_format = UPayloadFormat.UPAYLOAD_FORMAT_SOMEIP
                else:
                    any_obj = any_pb2.Any()
                    any_obj.Pack(message)
                    payload_data = any_obj.SerializeToString()
                    payload_format = UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF_WRAPPED_IN_ANY
                payload = UPayload(
                    data=payload_data,
                    format=payload_format,
                )
                method_uri = protobuf_autoloader.get_uuri_from_name(method_uri)

                upayload = self.tdk_apis.invoke_method(method_uri, payload, CallOptions(timeout=2000))
                sent_data = MessageToDict(message)

                message = "Successfully send rpc request for " + methodname
                if self.transport_config.get_transport() == "ZENOH":
                    message = "Successfully send rpc request for " + methodname + " to Zenoh"
                res = {"msg": message, "data": sent_data}
                self.socketio.emit(
                    constant.CALLBACK_SENDRPC,
                    res,
                    namespace=constant.NAMESPACE,
                )
                if upayload is not None:
                    response = await RpcMapper.map_response(upayload, res_cls)
                    common_handlers.rpc_response_handler(self.socketio, response)
            else:
                self.socketio.emit(
                    constant.CALLBACK_GENERIC_ERROR,
                    status,
                    namespace=constant.NAMESPACE,
                )

        except Exception:
            log = traceback.format_exc()
            self.socketio.emit(
                constant.CALLBACK_SENDRPC_EXC,
                log,
                namespace=constant.NAMESPACE,
            )

    async def execute_publish(self, json_publish):
        try:
            status = verify_all_checks(self.transport_config.get_transport_env())
            if status == "":
                topic = json_publish["topic"]
                data = json_publish["data"]
                service_class = json_publish["service_class"]

                json_data = json.loads(data)
                service_instance = get_service_instance_from_entity(service_class)
                if service_instance is not None:
                    message, status = await service_instance.publish(topic, json_data)
                    self.last_published_data = MessageToDict(message)
                    common_handlers.publish_status_handler(
                        self.socketio,
                        self.lock_pubsub,
                        self.transport_config.get_transport_env(),
                        topic,
                        status.code,
                        status.message,
                        self.last_published_data,
                    )

                    self.socketio.emit(
                        constant.CALLBACK_PUBLISH_STATUS_SUCCESS,
                        {
                            "msg": "Publish Data  ",
                            "data": self.last_published_data,
                        },
                        namespace=constant.NAMESPACE,
                    )

                else:
                    self.socketio.emit(
                        constant.CALLBACK_GENERIC_ERROR,
                        "Service is not running. Please start mock service.",
                        namespace=constant.NAMESPACE,
                    )

            else:
                self.socketio.emit(
                    constant.CALLBACK_GENERIC_ERROR,
                    status,
                    namespace=constant.NAMESPACE,
                )

        except Exception:
            log = traceback.format_exc()
            self.socketio.emit(
                constant.CALLBACK_EXCEPTION_PUBLISH,
                log,
                namespace=constant.NAMESPACE,
            )

    def configure_service_someip(self, json_service):
        configure_someip_service(json_service["entity"])
        self.socketio.emit(
            constant.CALLBACK_CONFIGURE_SOMEIP_SERVICE,
            {"entity": json_service["entity"], "status": True},
            namespace=constant.NAMESPACE,
        )

    async def start_mock_service(self, json_service):
        status = verify_all_checks(self.transport_config.get_transport_env())
        if status == "":

            def handler(rpc_request, method_name, json_data, rpcdata):
                common_handlers.rpc_logger_handler(
                    self.socketio,
                    self.lock_rpc,
                    rpc_request,
                    method_name,
                    json_data,
                    rpcdata,
                )

            try:
                status = await start_service(json_service["entity"], handler, self.transport_config, self.tdk_apis)
                self.socketio.emit(
                    constant.CALLBACK_START_SERVICE,
                    {"entity": json_service["entity"], "status": status},
                    namespace=constant.NAMESPACE,
                )
            except Exception as ex:
                logger.error("Exception:", exc_info=ex)
        else:
            print(status)

    async def execute_subscribe(self, json_subscribe):
        topic = json_subscribe["topic"]
        try:
            status = verify_all_checks(self.transport_config.get_transport_env())
            if status == "":
                new_topic = protobuf_autoloader.get_uuri_from_name(topic)

                status = await self.tdk_apis.register_listener(
                    new_topic,
                    SubscribeUListener(
                        self.socketio,
                        self.transport_config.get_transport_env(),
                        self.lock_pubsub,
                    ),
                )
                if status is None:
                    common_handlers.subscribe_status_handler(
                        self.socketio,
                        self.lock_pubsub,
                        self.transport_config.get_transport_env(),
                        topic,
                        0,
                        "Ok",
                    )
                else:
                    common_handlers.subscribe_status_handler(
                        self.socketio,
                        self.lock_pubsub,
                        self.transport_config.get_transport_env(),
                        topic,
                        status.code,
                        status.message,
                    )

            else:
                self.socketio.emit(
                    constant.CALLBACK_GENERIC_ERROR,
                    status,
                    namespace=constant.NAMESPACE,
                )

        except Exception:
            log = traceback.format_exc()
            self.socketio.emit(
                constant.CALLBACK_EXCEPTION_SUBSCRIBE,
                log,
                namespace=constant.NAMESPACE,
            )


class SubscribeUListener(UListener):
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, socketio: SocketIO, utransport: str, lock_pubsub: threading.Lock):
        if not self._initialized:
            self.__socketio = socketio
            self.__utransport_name = utransport
            self.__lock_pubsub = lock_pubsub
            self._initialized = True

    async def on_receive(self, msg: UMessage):
        print("onreceive")
        common_handlers.on_receive_event_handler(
            self.__socketio,
            self.__lock_pubsub,
            self.__utransport_name,
            self.convert_hex_to_int_in_string(UriSerializer.serialize(msg.attributes.source)),
            UPayload.pack_from_data_and_format(msg.payload, msg.attributes.payload_format),
        )
        return None

    def convert_hex_to_int_in_string(self, stri: str):
        segments = stri.split('/')
        new_segments = []

        for segment in segments:
            if segment:  # Check if segment is not empty
                try:
                    # Try to interpret the segment as a hexadecimal value
                    int_value = int(segment, 16)
                    new_segments.append(str(int_value))
                except ValueError:
                    # If it's not a hex value, keep it as is
                    new_segments.append(segment)
            else:
                new_segments.append(segment)

        return '/'.join(new_segments)
