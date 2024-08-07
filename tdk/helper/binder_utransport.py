"""
SPDX-FileCopyrightText: 2024 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

import base64
import json
import socket
import threading
import time
import traceback
from builtins import str
from concurrent.futures import Future, ThreadPoolExecutor
from sys import platform

from uprotocol.communication.calloptions import CallOptions
from uprotocol.communication.rpcclient import RpcClient
from uprotocol.communication.upayload import UPayload
from uprotocol.transport.builder.umessagebuilder import UMessageBuilder
from uprotocol.transport.ulistener import UListener
from uprotocol.transport.utransport import UTransport
from uprotocol.uri.serializer.uriserializer import UriSerializer
from uprotocol.uri.validator.urivalidator import UriValidator
from uprotocol.uuid.factory.uuidfactory import Factories
from uprotocol.uuid.serializer.uuidserializer import UuidSerializer
from uprotocol.v1.uattributes_pb2 import UMessageType
from uprotocol.v1.ucode_pb2 import UCode
from uprotocol.v1.umessage_pb2 import UMessage
from uprotocol.v1.uri_pb2 import UUri
from uprotocol.v1.ustatus_pb2 import UStatus

from tdk.utils.constant import REPO_URL

# Dictionary to store requests
m_requests = {}
subscribers = {}  # remove element when ue unregister it
r_services = {}  # running services
u_status = {}  # status update mapping with status id
MAX_MESSAGE_SIZE = 32767


# Function to add a request
def add_request(req_id: str):
    global m_requests
    future = Future()
    m_requests[req_id] = future
    return future


def status_update(s_id: str) -> UStatus:
    status_event = threading.Event()
    global u_status
    u_status[s_id] = status_event
    # Wait for the status to return with a timeout of 10 seconds
    if status_event.wait(timeout=10):
        event, status = u_status.get(s_id)
    else:
        status = UStatus(code=UCode.UNKNOWN, message="Error: Timeout reached")
    u_status.pop(s_id, None)
    return status


def timeout_counter(response_future, reqid, timeout):
    time.sleep(timeout / 1000)
    if not response_future.done():
        response_future.set_exception(
            TimeoutError("Not received response for request " + reqid + " within " + str(timeout / 1000) + " seconds")
        )


class SocketClient:
    _instance = None
    _create_topic_status_callbacks = {}

    def __add_create_topic_status_callback(self, topic, callback):
        if topic in self._create_topic_status_callbacks:
            callbacks = self._create_topic_status_callbacks[topic]
            if callback not in callbacks:
                callbacks.append(callback)
        else:
            callbacks = [callback]
            self._create_topic_status_callbacks[topic] = callbacks

    def register_create_topic_status_callback(self, topics, status_callback):
        if isinstance(topics, str):
            self.__add_create_topic_status_callback(topics, status_callback)
        else:
            for topic in topics:
                self.__add_create_topic_status_callback(topic, status_callback)

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SocketClient, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_address = ("127.0.0.1", 6095)
            self.connected = False
            self.initialized = True
            self._subscribe_callbacks = {}
            self._rpc_request_callbacks = {}
            self.received_data = None

    def connect(self):
        try:
            if not self.connected:
                self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.client_socket.connect(self.server_address)
                self.connected = True
                print("socket connected")
                receive_thread = threading.Thread(target=self.__receive_data)
                receive_thread.start()
                time.sleep(2)
        except Exception:
            log = traceback.format_exc()
            print("connect method exception", log)
            pass

    def __process_data(self, json_data):
        if "action" in json_data:
            action = json_data["action"]
            serialized_data = SocketTransport.serialize(json_data["data"])

            if action in ["topic_update", "rpc_request"]:
                parsed_message = UMessage()
                parsed_message.ParseFromString(serialized_data)
                if action == "topic_update":
                    uri_str = UriSerializer.serialize(parsed_message.attributes.source)

                    if uri_str in self.subscribe_callbacks:
                        callbacks = self.subscribe_callbacks[uri_str]
                        for callback in callbacks:
                            callback.on_receive(parsed_message)
                    else:
                        print(f"No callback registered for uri: {uri_str}. Discarding!")
                else:
                    uri_str = UriSerializer.serialize(parsed_message.attributes.sink)
                    if uri_str in self.rpc_request_callbacks:
                        callback = self.rpc_request_callbacks[uri_str]
                        callback.on_receive(parsed_message)
                    else:
                        print(f"No callback registered for uri: {uri_str}. Discarding!")

            elif action in [
                "publish_status",
                "subscribe_status",
                "register_rpc_status",
                "send_rpc_status",
            ]:
                parsed_message = UStatus()
                parsed_message.ParseFromString(serialized_data)
                if "status_id" in json_data:
                    status_id = json_data.get("status_id")
                    if status_id in u_status:
                        event = u_status[status_id]
                        u_status[status_id] = (event, parsed_message)
                        event.set()
            elif action == "rpc_response":
                parsed_message = UMessage()
                parsed_message.ParseFromString(serialized_data)
                req_id = UuidSerializer.serialize(parsed_message.attributes.reqid)
                future_result = m_requests[req_id]
                if not future_result.done():
                    future_result.set_result(parsed_message)
                else:
                    print("Future result state is already finished or cancelled")
                m_requests.pop(req_id)

            elif action in ["create_topic_status"]:
                print("create topic status called")

                parsed_message = UStatus()
                parsed_message.ParseFromString(serialized_data)
                topic_uri_str = json_data["topic"]
                if topic_uri_str in self._create_topic_status_callbacks:
                    print(f"create topic status called {topic_uri_str}")
                    callbacks = self._create_topic_status_callbacks[topic_uri_str]
                    for callback in callbacks:
                        callback(
                            topic_uri_str,
                            parsed_message.code,
                            parsed_message.message,
                        )
                else:
                    print(f"No create topic callback registered for uri: {topic_uri_str}. Discarding!")
            elif action == "start_service":
                parsed_message = UStatus()
                parsed_message.ParseFromString(serialized_data)
                service_name = parsed_message.message
                if service_name in r_services:
                    event, status = r_services[service_name]
                    if parsed_message.code == UCode.OK or parsed_message.code == UCode.ALREADY_EXISTS:
                        r_services[service_name] = (event, True)
                    event.set()

    def __receive_data(self):
        executor = ThreadPoolExecutor(max_workers=8)
        buffered_data = b''
        while self.connected:
            try:
                if platform == "linux" or platform == "linux2":
                    received_data = self.client_socket.recv(MAX_MESSAGE_SIZE, socket.MSG_DONTWAIT)
                else:
                    received_data = self.client_socket.recv(MAX_MESSAGE_SIZE)
                for formatted_data in received_data.splitlines():
                    buffered_data = buffered_data + formatted_data
                    if buffered_data != "":
                        data = buffered_data.decode("utf-8")

                        json_data = json.loads(data)
                        executor.submit(self.__process_data, json_data)
                        buffered_data = b''

                        print(f"Received from server: {json_data}")
            except (socket.timeout, OSError):
                pass
            except json.decoder.JSONDecodeError:
                pass

    def send_data(self, message):
        try:
            self.client_socket.sendall(message.encode("utf-8"))
            return True

        except Exception:
            self.disconnect()
            self.connect()
            try:
                self.client_socket.sendall(message.encode("utf-8"))
                return True
            except Exception:
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


class SocketTransport(UTransport, RpcClient):
    async def close(self) -> None:
        pass

    def get_source(self) -> UUri:
        return self.source

    def __init__(self, source: UUri):
        self.client = SocketClient()
        self.source = source
        # Start a separate thread for receiving

    def start_service(self, entity) -> bool:
        # write data to socket, this action will start the android mock service and create all topics
        json_map = {"action": "start_service", "data": entity}
        message_to_send = json.dumps(json_map) + "\n"
        start_service_event = threading.Event()
        global r_services
        # Update the service status with start_service_event set to False initially
        r_services.update({entity: (start_service_event, False)})
        self.client.send_data(message_to_send)
        # Wait for the service to start with a timeout of 10 seconds
        if start_service_event.wait(timeout=10) and r_services.get(entity)[1]:
            print(f"started service: {entity}")
            r_services.pop(entity, None)
            return True
        if start_service_event.is_set():
            print(f"unable to start service {entity}")
        else:
            print(f"unable to start service {entity} within timeout")
        r_services.pop(entity, None)
        return False

    def create_topic(self, entity, topics, status_callback):
        self.client.register_create_topic_status_callback(topics, status_callback)
        json_map = {"action": "create_topic", "data": entity, "topics": topics}
        message_to_send = json.dumps(json_map) + "\n"
        return self.client.send_data(message_to_send)

    def unregister_listener(self, uri: UUri, listener: UListener) -> UStatus:
        uri.entity.ClearField("id")
        uri.entity.ClearField("version_minor")
        uri.resource.ClearField("id")
        pass

    def send(self, umsg: UMessage) -> UStatus:
        global json_map
        self.client.connect()
        umsg.attributes.source.entity.ClearField("id")
        umsg.attributes.source.entity.ClearField("version_minor")
        umsg.attributes.source.resource.ClearField("id")

        if umsg.attributes.HasField("sink"):
            umsg.attributes.sink.entity.ClearField("id")
            umsg.attributes.sink.entity.ClearField("version_minor")
            if not UriValidator.is_rpc_response(umsg.attributes.sink):
                umsg.attributes.sink.resource.ClearField("id")
        message_str = SocketTransport.deserialize(umsg.SerializeToString())
        attributes = umsg.attributes
        topic = attributes.source
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
            message_to_send = json.dumps(json_map) + "\n"
            self.client.send_data(message_to_send)
            if attributes.type == UMessageType.UMESSAGE_TYPE_PUBLISH:
                return status_update(str(attributes.id))
            return

        except Exception as e:
            return UStatus(message=str(e), code=UCode.UNKNOWN)

    def register_listener(self, uri: UUri, listener: UListener) -> UStatus:
        self.client.connect()
        uri.entity.ClearField("id")
        uri.entity.ClearField("version_minor")
        uri.resource.ClearField("id")

        uri_str = SocketTransport.deserialize(uri.SerializeToString())

        try:
            status_id = str(Factories.UPROTOCOL.create())
            uri_key = UriSerializer.serialize(uri)
            if UriValidator.is_rpc_method(uri):
                self.__add_rpc_request_callback(uri_key, listener)
                # write data to socket
                json_map = {"action": "register_rpc", "data": uri_str, "status_id": status_id}
                print("register rpc for ", uri)
            else:
                self.__add_subscribe_callback(uri_key, listener)
                # write data to socket
                json_map = {"action": "subscribe", "data": uri_str, "status_id": status_id}
                print("subscribe to ", uri)

            message_to_send = json.dumps(json_map) + "\n"
            self.client.send_data(message_to_send)
            return status_update(status_id)

        except Exception as e:
            return UStatus(message=str(e), code=UCode.UNKNOWN)

    def invoke_method(self, method_uri: UUri, payload: UPayload, calloptions: CallOptions) -> Future:
        if method_uri is None or method_uri == UUri():
            raise Exception("Method Uri is empty")
        if payload is None:
            raise Exception("Payload is None")
        if calloptions is None:
            raise Exception("CallOptions cannot be None")
        timeout = calloptions.timeout
        if timeout <= 0:
            raise Exception("TTl is invalid or missing")
        umsg = UMessageBuilder.request(self.get_source(), method_uri, timeout).build_from_upayload(payload)
        if "COVESA" not in REPO_URL:
            umsg.attributes.id.MergeFrom(Factories.UUIDV6.create())
        # check message type,id and ttl
        req_id = UuidSerializer.serialize(umsg.attributes.id)
        response_future = add_request(req_id)

        self.send(umsg)
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
        self.client.rpc_request_callbacks[method_uri] = callback

    @staticmethod
    def serialize(string_to_serialize: str) -> bytes:
        """
        Serialize a String into Base64 format.<br><br>
        @param string_to_serialize:String to serialize.
        @return: Returns the Base64 formatted String as a byte[].
        """
        if string_to_serialize is None:
            return bytearray()
        return base64.b64decode(string_to_serialize.encode('utf-8'))

    @staticmethod
    def deserialize(proto_bytes: bytes) -> str:
        """
        Deserialize a base64 protobuf payload into a Base64 String.<br><br>

        @param proto_bytes: byte[] data
        @return: Returns a String from the base64 protobuf payload.
        """
        if proto_bytes is None:
            return ""
        return base64.b64encode(proto_bytes).decode('utf-8')
