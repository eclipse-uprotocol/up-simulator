# -------------------------------------------------------------------------
import json
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

# -------------------------------------------------------------------------


import socket
import threading
import time
from builtins import str
from concurrent.futures import Future

from uprotocol.cloudevent.serialize.base64protobufserializer import Base64ProtobufSerializer
from uprotocol.proto.uattributes_pb2 import UAttributes, UMessageType
from uprotocol.proto.umessage_pb2 import UMessage

from uprotocol.proto.upayload_pb2 import UPayload
from uprotocol.proto.uri_pb2 import UEntity, UUri
from uprotocol.proto.ustatus_pb2 import UStatus, UCode
from uprotocol.rpc.rpcclient import RpcClient
from uprotocol.transport.ulistener import UListener
from uprotocol.transport.utransport import UTransport
from uprotocol.uri.validator.urivalidator import UriValidator

# Dictionary to store requests
m_requests = {}
m_requests_query = {}
subscribers = {}  # remove element when ue unregister it
register_rpc_querable = {}  # remove element when ue unregister it


# Function to add a request
def add_request(req_id: str):
    global m_requests
    future = Future()
    m_requests[req_id] = future
    return future


def timeout_counter(response_future, reqid, timeout):
    time.sleep(timeout / 1000)
    if not response_future.done():
        response_future.set_exception(
            TimeoutError('Not received response for request ' + reqid + ' within ' + str(timeout / 1000) + ' seconds'))


class SocketClient:
    _instance = None
    MAX_MESSAGE_SIZE = 32767

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SocketClient, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_address = ('127.0.0.1', 6095)
            self.connected = False
            self.initialized = True

    def connect(self):
        self.client_socket.connect(self.server_address)
        self.connected = True

    def receive_data(self):
        while self.connected:
            try:
                received_data = self.client_socket.recv(self.MAX_MESSAGE_SIZE)
                if not received_data:
                    break
                received_data = received_data.decode('utf-8')
                print(f"Received from server: {received_data}")
                print(Base64ProtobufSerializer().serialize(received_data))
            except socket.error:
                break

    def send_data(self, message):
        self.client_socket.sendall(message.encode('utf-8'))

    def start(self):
        # Connect to the server
        self.connect()

        # Start a separate thread for receiving
        receive_thread = threading.Thread(target=self.receive_data)
        receive_thread.start()


client = SocketClient()
client.start()


class AndroidBinder(UTransport):

    def __init__(self):
        pass

    def register_listener(self, topic: UUri, listener: UListener) -> UStatus:
        pass

    def unregister_listener(self, topic: UUri, listener: UListener) -> UStatus:
        pass

    def authenticate(self, u_entity: UEntity) -> UStatus:
        print("unimplemented, it is not needed in python components.")

    def send(self, topic: UUri, payload: UPayload, attributes: UAttributes) -> UStatus:

        # validate attributes
        if attributes.type == UMessageType.UMESSAGE_TYPE_PUBLISH:
            # check uri
            status = UriValidator.validate(topic)
            if status.is_failure():
                return status
            # create publish cloudevent
            umsg = UMessage(source=topic, attributes=attributes, payload=payload)
            message_str = Base64ProtobufSerializer().deserialize(umsg.SerializeToString())
            try:
                # write data to socket
                json_map = {"action": "send", "data": message_str}
                message_to_send = json.dumps(json_map) + '\n'
                client.send_data(message_to_send)
                return UStatus(message="successfully publish value to zenoh_up")
            except Exception as e:
                print('failed')
                return UStatus(message=str(e), code=UCode.UNKNOWN)

        # elif attributes.type == UMessageType.UMESSAGE_TYPE_REQUEST:
        #     # check uri
        #     status = UriValidator.validate_rpc_method(topic)
        #     if status.is_failure():
        #         return status
        #
        #     # create request cloudevent
        #     ce, serialized_str = ZenohUtils.create_serialized_ce(topic, payload, attributes)
        #     ZenohUtils().send_rpc_request_zenoh(UCloudEvent.get_sink(ce), serialized_str)
        #
        # elif attributes.type == UMessageType.UMESSAGE_TYPE_RESPONSE:
        #     status = UriValidator.validate_rpc_method(topic)
        #     if status.is_failure():
        #         return status
        #
        #     # create response cloudevent
        #     ce, serialized_str = ZenohUtils.create_serialized_ce(topic, payload, attributes)
        #     print('response ')
        #     methoduri = ZenohUtils.replace_special_chars(LongUriSerializer().serialize(topic))
        #     m_requests_query[UCloudEvent.get_request_id(ce)].reply(Sample(methoduri, serialized_str))
        #     m_requests_query.pop(UCloudEvent.get_request_id(ce))
        #     return UStatus(message="successfully send rpc response to zenoh")

        else:
            return UStatus(message="Invalid attributes type")
