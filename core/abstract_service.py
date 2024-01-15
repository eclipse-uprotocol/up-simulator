# Copyright (C) GM Global Technology Operations LLC 2022-2023.
# All Rights Reserved.
# GM Confidential Restricted.

"""
CovesaService class for class-based mock services. Class-based services inherit
from this class and a static method decorator is used to define RPC
handlers. Methods defined in a child class must be named the same as the RPC
method and decorated with the :code:@CovesaService.rpc_handler decorator. The decorated
method will be registered automatically and called when the rpc method is 
invoked. The parameters to an rpc_handler are the request protobuf object and 
response protobuf object. The request protobuf will be automatically populated 
with the request data. The response object will be a protobuf object of the 
type returned by the rpc method and should be returned by the function. The 
response will be sent when the handler returns. See rpc_send_example.py for a 
basic example. This also decouples rpc methods and services; rpc methods from
multiple services can be combined into a single class.
"""

import os
import pickle
import re
import signal
import time
from pathlib import Path
from sys import platform, exit
from threading import Thread, current_thread, main_thread
from uprotocol.proto.upayload_pb2 import UPayload
from uprotocol.proto.uattributes_pb2 import UAttributes, UMessageType, UPriority
from uprotocol.proto.upayload_pb2 import UPayloadFormat
from google.protobuf import text_format, any_pb2
from uprotocol.uuid.factory.uuidfactory import Factories
from uprotocol.proto.ustatus_pb2 import UStatus
from uprotocol.uuid.serializer.longuuidserializer import LongUuidSerializer

from utils import common_util
from uprotocol.rpc.rpcmapper import RpcMapper
from uprotocol.transport.builder.uattributesbuilder import UAttributesBuilder
from uprotocol.uri.serializer.longuriserializer import LongUriSerializer
from uprotocol.proto.uri_pb2 import UUri

from core.exceptions import SimulationError

from core.transport_layer import TransportLayer
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
        common_util.common_publish_status_handler(self.uri, status.code, status.message)
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

    # def loadRpcMethods(self, service_name):
    #     """
    #     Interal method to load rpc method data.
    #
    #     Args:
    #         service_name (str): String to identify COVESA service
    #     """
    #     methods = protobuf_autoloader.get_methods_by_service(service_name)
    #     if service_name not in self.rpc_methods.keys():
    #         self.rpc_methods[service_name] = {}
    #     # for method in methods.keys():
    #     #     self.rpc_methods[service_name][method] = ResponseReceivedCallback(method, methods[method]["request"],
    #     #                                                                       methods[method]["response"],
    #     #                                                                       methods[method]["uri"],
    #     #                                                                       # methods[method]["versions"],
    #     #                                                                       self.rpc, self)
    #
    # def addRpcResponseHandler(self, rpc_class):
    #     """
    #     Adds an custom class for rpc response handling.
    #
    #     Args:
    #         rpc_class (): Class representing remote procedure call
    #     """
    #     if self.service == None:
    #         print("You must set the service name in the CovesaService constructor or via CovesaService.setService()")
    #         raise SimulationError("service_name not specified when registering response handler.")
    #     for attr in dir(rpc_class):
    #         if (callable(getattr(rpc_class, attr)) and getattr(rpc_class, attr).__name__ in
    #                 protobuf_autoloader.rpc_methods[
    #                     self.service].keys()):
    #             method_name = getattr(rpc_class, attr).__name__
    #             request = protobuf_autoloader.get_request_class(self.service, method_name)
    #             response = protobuf_autoloader.get_response_class(self.service, method_name)
    #             uri = protobuf_autoloader.get_rpc_uri_by_name(self.service, method_name)
    #             self.rpc_methods[self.service][method_name] = rpc_class(method_name, request, response, uri, self.rpc,
    #                                                                     self)
    #
    # def invokeMethod(self, method_name, params={}, version=1):
    #     """
    #     Calls an rpc method.
    #
    #     Args:
    #         method_name (str): Name of rpc method
    #         params (dictionary, Optional): Dictionary of parameters for rpc method (default is an empty dictionary)
    #         version (int): The version of the API to use (Not available yet, WIP)
    #     """
    #     if self.service == None:
    #         print("You must set the service name in the CovesaService constructor or via CovesaService.setService()")
    #         raise SimulationError("service_name not specified when sending RPC request.")
    #     for param in params.keys():
    #         self.rpc_methods[self.service][method_name].setParam(param, params[param])
    #     self.rpc_methods[self.service][method_name].send(version)
    #     return self.rpc_methods[self.service][method_name]

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
            common_util.common_subscribe_status_handler(uri, 0, "OK")
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
