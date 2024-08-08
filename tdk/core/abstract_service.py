"""
SPDX-FileCopyrightText: 2024 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

import asyncio
import os
import pickle
import signal
import time
from pathlib import Path
from sys import exit, platform
from threading import current_thread, main_thread

from google.protobuf import any_pb2, text_format
from uprotocol.communication.upayload import UPayload
from uprotocol.uuid.factory.uuidfactory import Factories
from uprotocol.v1.uattributes_pb2 import UPayloadFormat
from uprotocol.v1.umessage_pb2 import UMessage

from tdk.apis.apis import TdkApis
from tdk.core import protobuf_autoloader
from tdk.helper.transport_configuration import TransportConfiguration
from tdk.utils import service_util
from tdk.utils.constant import REPO_URL
from tdk.utils.service_util import SimulationError

covesa_services = []


def get_instance(service_id):
    if not isinstance(service_id, str):
        service_id = str(service_id)
    for entity_dict in covesa_services:
        if entity_dict.get('id') == service_id:
            return entity_dict.get('entity')


class BaseService(object):
    def __init__(
        self,
        service_name=None,
        portal_callback=None,
        transport_config: TransportConfiguration = None,
        tdk_apis: TdkApis = None,
        use_signal_handler=True,
    ):
        self.service = service_name
        self.service_id = protobuf_autoloader.get_entity_id_from_entity_name(service_name)
        self.subscriptions = {}
        self.portal_callback = portal_callback
        if transport_config is None or tdk_apis is None:
            self.transport_config = TransportConfiguration()
            self.tdk_apis = TdkApis(self.transport_config)
        else:
            self.tdk_apis = tdk_apis
            self.transport_config = transport_config
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

    def request_listener(self):
        class Wrapper:
            @staticmethod
            def handle_request(message: UMessage):
                global instance
                print('Wrapper on receive')
                attributes = message.attributes
                topic_uri = attributes.sink
                service_id = topic_uri.ue_id
                method_id = topic_uri.resource_id
                method_name = protobuf_autoloader.get_method_name_from_method_id(service_id, method_id)
                payload = message.payload
                req = protobuf_autoloader.get_request_class(service_id, method_name)
                res = protobuf_autoloader.get_response_class(service_id, method_name)()
                req = UPayload.unpack_data_format(payload, attributes.payload_format, req)
                response = self(get_instance(service_id), req, res)

                payload_res: UPayload = UPayload.pack_to_any(response)

                if get_instance(service_id).portal_callback is not None:
                    get_instance(service_id).portal_callback(
                        req, method_name, response, get_instance(service_id).publish_data
                    )

                return payload_res

        return Wrapper

    async def start_rpc_service(self) -> bool:
        if self.transport_config.start_service(self.service):
            covesa_services.append({'id': self.service_id, 'entity': self})
            # create topic
            topics = protobuf_autoloader.get_topics_by_proto_service_id(self.service_id)
            # for topic in topics:
            if len(topics) >= 0:
                self.transport_config.create_topic(self.service, topics, service_util.print_create_topic_status_handler)
            for attr in dir(self):
                if callable(getattr(self, attr)) and isinstance(getattr(self, attr), type):
                    for attr1 in dir(getattr(self, attr)):
                        if attr1 == 'handle_request':
                            func = getattr(self, attr)
                            method_uri_str = protobuf_autoloader.get_rpc_uri_by_name(self.service_id, attr)
                            method_uri = protobuf_autoloader.get_uuri_from_name(method_uri_str)

                            status = await self.tdk_apis.register_request_handler(method_uri, func)
                            service_util.print_register_rpc_status(method_uri_str, status.code, status.message)

                            break
            await self.subscribe()
            return True
        else:
            return False

    async def publish(self, uri, params={}, is_from_rpc=False):
        message_class = protobuf_autoloader.get_request_class_from_topic_uri(uri)
        message = protobuf_autoloader.populate_message(self.service, message_class, params)
        any_obj = any_pb2.Any()
        any_obj.Pack(message)
        payload_data = any_obj.SerializeToString()
        payload = UPayload(format=UPayloadFormat.UPAYLOAD_FORMAT_PROTOBUF_WRAPPED_IN_ANY, data=payload_data)
        source_uri = protobuf_autoloader.get_uuri_from_name(uri)

        if "COVESA" not in REPO_URL:
            message.attributes.id = Factories.UUIDV6.create()
        status = await self.tdk_apis.publish(topic=source_uri, payload=payload)
        service_util.print_publish_status(uri, status.code, status.message)
        if is_from_rpc:
            self.publish_data.clear()
            self.publish_data.append(message)
        await asyncio.sleep(0.25)
        return message, status

    async def subscribe(self, uris=None, listener=None):
        if uris is None or listener is None:
            return
        for uri in uris:
            if uri in self.subscriptions.keys() and listener == self.subscriptions[uri]:
                print(f"Warning: there already exists an object subscribed to {uri}")
                print(f"Skipping subscription for {uri}")
            self.subscriptions[uri] = listener
            topic_uri = protobuf_autoloader.get_uuri_from_name(uri)
            status = await self.tdk_apis.register_listener(topic_uri, listener)
            service_util.print_subscribe_status(uri, status.code, status.message)
            await asyncio.sleep(1)

    async def start(self) -> bool:
        if self.service is None:
            print("Unable to start mock service without specifying the service name.")
            print("You must set the service name in the BaseService constructor")
            raise SimulationError("service_name not specified for mock service")
        print("Waiting for events...")

        return await self.start_rpc_service()

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
        except OSError:
            print("Unable to save state.")

    def load_state(self):
        try:
            print("Loading previous state...")
            with open(self.state_file, "rb") as f:  # "rb" because we want to read in binary mode
                self.state = pickle.load(f)
            print("Done!")
        except OSError:
            print("Unable to load previous state.")
