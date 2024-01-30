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
import socket
import threading
import time
import traceback
from builtins import str
from concurrent.futures import Future
from sys import platform

from uprotocol.cloudevent.serialize.base64protobufserializer import Base64ProtobufSerializer
from uprotocol.proto.uattributes_pb2 import UAttributes, UMessageType
from uprotocol.proto.umessage_pb2 import UMessage
from uprotocol.proto.upayload_pb2 import UPayload
from uprotocol.proto.uri_pb2 import UEntity, UUri
from uprotocol.proto.ustatus_pb2 import UStatus, UCode
from uprotocol.rpc.rpcclient import RpcClient
from uprotocol.transport.ulistener import UListener
from uprotocol.transport.utransport import UTransport
from uprotocol.uri.serializer.longuriserializer import LongUriSerializer
from uprotocol.uri.validator.urivalidator import UriValidator
from uprotocol.uuid.serializer.longuuidserializer import LongUuidSerializer

# Dictionary to store requests
m_requests = {}
subscribers = {}  # remove element when ue unregister it
MAX_MESSAGE_SIZE = 32767


# Function to add a request
def add_request(req_id: str):
    global m_requests
    future = Future()
    print('Neel', req_id)
    m_requests[req_id] = future
    return future


def timeout_counter(response_future, reqid, timeout):
    time.sleep(timeout / 1000)
    if not response_future.done():
        response_future.set_exception(
            TimeoutError('Not received response for request ' + reqid + ' within ' + str(timeout / 1000) + ' seconds'))


class SocketClient:
    _instance = None

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
            self._subscribe_callbacks = {}
            self._rpc_request_callbacks = {}
            self.receive_lock = threading.Lock()
            self.received_data = None

    def receive_data(self):
        start_time = time.time()
        while True:
            with self.receive_lock:
                if self.received_data is not None:
                    data = self.received_data
                    self.received_data = None
                    return data
            if time.time() - start_time > 11:
                return UStatus(code=UCode.UNKNOWN, message="Error: Timeout reached")
            time.sleep(0.1)  # Adjust sleep time as needed to reduce CPU load

    def handle_received_data(self, data):
        with self.receive_lock:
            self.received_data = data

    def connect(self):
        try:
            if not self.connected:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect(self.server_address)
                self.connected = True
                print('socket connected')
                receive_thread = threading.Thread(target=self.__receive_data)
                receive_thread.start()
                time.sleep(2)
        except:
            log = traceback.format_exc()
            print('connect method exception', log)
            pass

    def __receive_data(self):
        buffered_data = None
        BUFFER_FLAG = False
        while self.connected:
            try:
                if platform == "linux" or platform == "linux2":
                    received_data = self.client_socket.recv(MAX_MESSAGE_SIZE, socket.MSG_DONTWAIT)
                else:
                    received_data = self.client_socket.recv(MAX_MESSAGE_SIZE)
                for formatted_data in received_data.splitlines():
                    if BUFFER_FLAG:
                        formatted_data = buffered_data + formatted_data
                        BUFFER_FLAG = False
                    else:
                        buffered_data = formatted_data
                    if formatted_data != '':
                        data = formatted_data.decode('utf-8')

                        json_data = json.loads(data)
                        if 'action' in json_data:
                            action = json_data['action']
                            serialized_data = Base64ProtobufSerializer().serialize(json_data['data'])

                            if action in ["topic_update", "rpc_request"]:
                                parsed_message = UMessage()
                                parsed_message.ParseFromString(serialized_data)
                                if action == "topic_update":
                                    uri_str = LongUriSerializer().serialize(parsed_message.source)
                                    uri = parsed_message.source
                                    action_callbacks = self.subscribe_callbacks
                                else:
                                    uri_str = LongUriSerializer().serialize(parsed_message.attributes.sink)
                                    uri = parsed_message.attributes.sink
                                    action_callbacks = self.rpc_request_callbacks
                                if uri_str in action_callbacks:
                                    callbacks = action_callbacks[uri_str]
                                    for callback in callbacks:
                                        callback.on_receive(uri, parsed_message.payload, parsed_message.attributes)
                                else:
                                    print(f'No callback registered for uri: {uri_str}. Discarding!')

                            elif action in ["publish_status", "subscribe_status", "register_rpc_status",
                                            "send_rpc_status"]:
                                parsed_message = UStatus()
                                parsed_message.ParseFromString(serialized_data)
                                self.handle_received_data(parsed_message)
                            elif action == "rpc_response":
                                parsed_message = UMessage()
                                parsed_message.ParseFromString(serialized_data)
                                req_id = LongUuidSerializer.instance().serialize(parsed_message.attributes.reqid)
                                future_result = m_requests[req_id]
                                if not future_result.done():
                                    future_result.set_result(parsed_message.payload)
                                else:
                                    print("Future result state is already finished or cancelled")
                                m_requests.pop(req_id)

                        print(f"Received from server: {json_data}")
            except (socket.timeout, OSError):
                pass
            except json.decoder.JSONDecodeError:
                BUFFER_FLAG = True

    def send_data(self, message):

        try:
            self.client_socket.sendall(message.encode('utf-8'))
            return True

        except:
            self.disconnect()
            self.connect()
            try:
                self.client_socket.sendall(message.encode('utf-8'))
                return True
            except:
                return False

    def disconnect(self):
        # close socket
        self.client_socket.close()
        self.connected = False

    def __del__(self):
        """
        Default destructor. Disconnects underlying socket connection with VCU target.
        """
        self.disconnect()

    @property
    def subscribe_callbacks(self):
        return self._subscribe_callbacks

    @property
    def rpc_request_callbacks(self):
        return self._rpc_request_callbacks


class AndroidBinder(UTransport, RpcClient):

    def __init__(self):
        self.client = SocketClient()

        # Start a separate thread for receiving

    def start_service(self, entity) -> bool:
        # write data to socket, this action will start the android mock service and create all topics
        json_map = {"action": "start_service", "data": entity}
        message_to_send = json.dumps(json_map) + '\n'
        return self.client.send_data(message_to_send)

    def unregister_listener(self, topic: UUri, listener: UListener) -> UStatus:
        pass

    def authenticate(self, u_entity: UEntity) -> UStatus:
        print("unimplemented, it is not needed in python components.")

    def send(self, topic: UUri, payload: UPayload, attributes: UAttributes) -> UStatus:
        global json_map
        self.client.connect()
        umsg = UMessage(source=topic, attributes=attributes, payload=payload)
        message_str = Base64ProtobufSerializer().deserialize(umsg.SerializeToString())
        # validate attributes
        if attributes.type == UMessageType.UMESSAGE_TYPE_PUBLISH:
            # check uri
            status = UriValidator.validate(topic)
            if status.is_failure():
                return status
            json_map = {"action": "publish", "data": message_str}

        elif attributes.type == UMessageType.UMESSAGE_TYPE_REQUEST:
            # check uri
            status = UriValidator.validate_rpc_method(topic)
            if status.is_failure():
                return status
            json_map = {"action": "send_rpc", "data": message_str}

        elif attributes.type == UMessageType.UMESSAGE_TYPE_RESPONSE:
            status = UriValidator.validate_rpc_method(topic)
            if status.is_failure():
                return status
            json_map = {"action": "rpc_response", "data": message_str}

        try:
            # write data to socket
            message_to_send = json.dumps(json_map) + '\n'
            self.client.send_data(message_to_send)
            received_data = None
            if attributes.type in [UMessageType.UMESSAGE_TYPE_PUBLISH]:
                # Wait for data to be received from the socket
                received_data = UStatus(message="Successfully publish", code=UCode.OK)#self.client.receive_data()
            return received_data

        except Exception as e:
            return UStatus(message=str(e), code=UCode.UNKNOWN)

    def register_listener(self, uri: UUri, listener: UListener) -> UStatus:
        self.client.connect()
        uri_str = Base64ProtobufSerializer().deserialize(uri.SerializeToString())

        try:
            if UriValidator.validate_rpc_method(uri).is_success():
                self.__add_rpc_request_callback(LongUriSerializer().serialize(uri), listener)
                # write data to socket
                json_map = {"action": "register_rpc", "data": uri_str}
                print('register rpc for ', uri)

            else:
                self.__add_subscribe_callback(LongUriSerializer().serialize(uri), listener)
                # write data to socket
                json_map = {"action": "subscribe", "data": uri_str}
                print('subscribe to ', uri)

            message_to_send = json.dumps(json_map) + '\n'
            self.client.send_data(message_to_send)
            # Wait for data to be received from the socket
            received_data = self.client.receive_data()
            return received_data
        except Exception as e:
            return UStatus(message=str(e), code=UCode.UNKNOWN)

    def invoke_method(self, topic: UUri, payload: UPayload, attributes: UAttributes) -> Future:
        # check message type,id and ttl
        req_id = LongUuidSerializer.instance().serialize(attributes.id)
        if attributes.type != UMessageType.UMESSAGE_TYPE_REQUEST:
            raise Exception("Event type is invalid")
        if req_id is None or len(req_id.strip()) == 0:
            raise Exception("Event id is missing")
        if attributes.ttl is None or attributes.ttl <= 0:
            raise Exception("TTl is invalid or missing")

        response_future = add_request(req_id)
        # # Start a thread to count the timeout
        # timeout_thread = threading.Thread(target=timeout_counter, args=(response_future, req_id, attributes.ttl))
        # timeout_thread.start()
        self.send(topic, payload, attributes)
        return response_future  # future result to be set by the service.

    def __add_subscribe_callback(self, topic: str, callback: UListener):
        """
        Checks if a topic is already subscribed or not and accordingly create mappings between topic and callback.
        If already subscribed, then adds the callback into the list of already registered callbacks.
        If it is a fresh subscription, then creates a new list of callbacks and adds to it.

        :param topic: A topic name to which subscription is to be made
        :param callback: This is a method that will be invoked upon receiving
        """
        if topic in self.client.subscribe_callbacks:
            callbacks = self.client.subscribe_callbacks[topic]
            if callback not in callbacks:
                callbacks.append(callback)
        else:
            callbacks = [callback]
            self.client.subscribe_callbacks[topic] = callbacks

    def __add_rpc_request_callback(self, method_uri: str, callback: UListener):

        if method_uri in self.client.rpc_request_callbacks:
            callbacks = self.client.rpc_request_callbacks[method_uri]
            if callback not in callbacks:
                callbacks.append(callback)
        else:
            callbacks = [callback]
            self.client.rpc_request_callbacks[method_uri] = callbacks
