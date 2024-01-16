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
from uprotocol.proto.uattributes_pb2 import UAttributes, UPriority
from uprotocol.proto.upayload_pb2 import UPayload
from uprotocol.proto.upayload_pb2 import UPayloadFormat
from uprotocol.proto.uri_pb2 import UUri
from uprotocol.proto.ustatus_pb2 import UStatus
from uprotocol.rpc.rpcmapper import RpcMapper
from uprotocol.transport.builder.uattributesbuilder import UAttributesBuilder
from uprotocol.uri.serializer.longuriserializer import LongUriSerializer

from core.exceptions import SimulationError
from core.transport_layer import TransportLayer
from utils import common_util
from utils import protobuf_autoloader


class Message(object):
    """
    Message class used to return status messages to the user via console.
    """

    def __init__(self, uri, full_name, message_class, service_name, transport):
        self.uri = uri
        self.transport = transport
        self.message_class = message_class
        self.full_name = full_name
        self.params = {}
        fields = protobuf_autoloader.get_message_fields(message_class)
        for field in fields:
            self.params[field] = None
        self.service = service_name

    def setParam(self, name, value):
        """
        Creates a new paramater in Message object's parameter dictionary.

        Args:
            name (str): Key for params dictionary 
            value (str): Value for params dictionary
        """
        self.params[name] = value

    def publish(self):
        """
        Returns message variable from Message object.
        Returns:
            string: Value from message_class
        """
        self.message = protobuf_autoloader.populate_message(self.service, self.message_class, self.params)
        any_obj = any_pb2.Any()
        any_obj.Pack(self.message)
        payload_data = any_obj.SerializeToString()
        payload = UPayload(value=payload_data, format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF)
        attributes = UAttributesBuilder.publish(UPriority.UPRIORITY_CS4).build()
        status = self.transport.send(LongUriSerializer().deserialize(self.uri), payload, attributes)
        common_util.print_publish_status(self.uri, status.code, status.message)
        return self.message


class CovesaService(object):
    instance = None

    def __init__(self, service_name=None, portal_callback=None, use_signal_handler=True):

        self.transport = TransportLayer()
        self.service = service_name
        self.messages = {}
        self.rpc_methods = {}
        if self.service is not None:
            self.loadMessageClasses(service_name)
        #     self.loadRpcMethods(service_name)
        self.subscriptions = {}
        self.portal_callback = portal_callback
        self.publish_data = []  # used by portal
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

    def set_instance(self):
        global instance
        instance = self

    @staticmethod
    def get_instance():
        global instance
        return instance

    def RequestListener(func):
        """
        Decorator for mock services. Returns a wrapper function.

        Args:
            func (function): A function 

        Returns:
            function: Value from message_class
        """
        setattr(func, "rpc_callback", True)

        class wrapper:
            @staticmethod
            def on_receive(topic: UUri, payload: UPayload, attributes: UAttributes) -> UStatus:
                global instance
                print('wrapper on receive')
                entity = topic.entity.name
                method = topic.resource.instance
                req = protobuf_autoloader.get_request_class(entity, method)
                res = protobuf_autoloader.get_response_class(entity, method)()
                any_message = any_pb2.Any()
                any_message.ParseFromString(payload.value)
                req = RpcMapper.unpack_payload(any_message, req)
                response = func(CovesaService.get_instance(), req, res)
                any_obj = any_pb2.Any()
                any_obj.Pack(response)
                payload_res = UPayload(value=any_obj.SerializeToString(), format=payload.format)
                attributes = UAttributesBuilder.response(attributes.priority, attributes.sink, attributes.id).build()
                if CovesaService.get_instance().portal_callback is not None:
                    CovesaService.get_instance().portal_callback(req, method, response,
                                                                 CovesaService.get_instance().publish_data)
                return TransportLayer().send(topic, payload_res, attributes)

        return wrapper

    def start_rpc_service(self):

        self.set_instance()
        for attr in dir(self):
            if callable(getattr(self, attr)) and isinstance(getattr(self, attr), type):
                for attr1 in dir(getattr(self, attr)):
                    if attr1 == 'on_receive':
                        func = getattr(self, attr)
                        method_uri = protobuf_autoloader.get_rpc_uri_by_name(self.service, attr)
                        self.transport.register_listener(LongUriSerializer().deserialize(method_uri), func)
                        break

    def loadMessageClasses(self, service_name):
        """
        Internal function to load message data.

        Args:
            service_name (str): String to identify Ultifi service
        """
        messages = protobuf_autoloader.get_topics_by_service(service_name)
        for message in messages:
            (uri, message_class) = message

            self.messages[str(uri)] = Message(uri, message_class.DESCRIPTOR.full_name, message_class, self.service,
                                              self.transport, )

    def publish(self, uri, params={}):

        for param in params.keys():
            self.messages[uri].setParam(param, params[param])
        ret = self.messages[uri].publish()
        self.publish_data.append(ret)
        time.sleep(0.25)
        return ret

    def subscribe(self, uris, listener):

        for uri in uris:
            if uri in self.subscriptions.keys() and listener == self.subscriptions[uri]:
                print(f"Warning: there already exists an object subscribed to {uri}")
                print(f"Skipping subscription for {uri}")
            self.subscriptions[uri] = listener
            self.transport.register_listener(LongUriSerializer().deserialize(uri), listener.on_receive)
            common_util.print_subscribe_status(uri, 0, "OK")
            time.sleep(1)

    def start(self):

        if self.service is None:
            print("Unable to start mock service without specifying the service name.")
            print("You must set the service name in the CovesaService constructor")
            raise SimulationError("service_name not specified for mock service")
        print("Waiting for events...")
        self.start_rpc_service()

        return self

    def disconnect(self):

        time.sleep(5)

    def print(self, protobuf_obj):
        """
        Prints a protobuf object. 

        Args:
            protobuf_obj (obj):  A protobuf object
        """
        print(f"Message: {protobuf_obj.DESCRIPTOR.full_name}")
        print(text_format.MessageToString(protobuf_obj))

    def signal_handler(self, sig, frame):
        """
        Signal handler to quit mock services.

        Args:
            sig (obj): A signal
            frame (obj): A frame
        """
        print("Exiting gracefully....")
        exit()

    def init_message_state(self, message_class):
        """
        Initialize a data structure for maintaining state for a message type

        Args:
            message_class (object):  A protobuf object.

        Returns:
            dict: A mapping of message fields: default value
        """
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
