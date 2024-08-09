"""
SPDX-FileCopyrightText: 2024 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

from typing import Optional

from up_transport_zenoh.uptransportzenoh import UPTransportZenoh
from uprotocol.client.usubscription.v3.inmemoryusubcriptionclient import InMemoryUSubscriptionClient
from uprotocol.client.usubscription.v3.subscriptionchangehandler import SubscriptionChangeHandler
from uprotocol.communication.calloptions import CallOptions
from uprotocol.communication.inmemoryrpcclient import InMemoryRpcClient
from uprotocol.communication.inmemoryrpcserver import InMemoryRpcServer
from uprotocol.communication.simplepublisher import SimplePublisher
from uprotocol.communication.upayload import UPayload
from uprotocol.core.usubscription.v3.usubscription_pb2 import (
    FetchSubscribersResponse,
    FetchSubscriptionsRequest,
    FetchSubscriptionsResponse,
    SubscriptionResponse,
)
from uprotocol.transport.ulistener import UListener
from uprotocol.uri.factory.uri_factory import UriFactory
from uprotocol.v1.uri_pb2 import UUri
from uprotocol.v1.ustatus_pb2 import UStatus

from tdk.helper.transport_configuration import TransportConfiguration

try:
    from uprotocol_vsomeip.vsomeip_utransport import (
        VsomeipTransport,
    )

except ImportError:
    pass


def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


@singleton
class TdkApis:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self, transport_config: TransportConfiguration):
        if not self.__initialized or self.__transport != transport_config.get_transport():
            self.initialize(transport_config.get_transport())
            self.__initialized = True

    def refresh_transport(self, transport_config: TransportConfiguration):
        if self.get_transport_env() != transport_config.get_transport_env():
            self.initialize(transport_config.get_transport())

    def get_transport_env(self) -> str:
        if isinstance(self.__transport, UPTransportZenoh):
            return "ZENOH"
        try:
            if isinstance(self.__transport, VsomeipTransport):
                return "SOME/IP"
        except Exception:
            pass

        return "BINDER"

    def initialize(self, transport):
        self.__transport = transport
        self.__subscription_client = InMemoryUSubscriptionClient(self.__transport)
        self.__rpc_server = InMemoryRpcServer(self.__transport)
        self.__publisher = SimplePublisher(self.__transport)
        self.__rpc_client = InMemoryRpcClient(self.__transport)

    async def subscribe(
        self,
        topic: UUri,
        listener: UListener,
        options: CallOptions = CallOptions.DEFAULT,
        handler: Optional[SubscriptionChangeHandler] = None,
    ) -> SubscriptionResponse:
        await self.__subscription_client.subscribe(topic, listener, options, handler)

    async def unsubscribe(
        self, topic: UUri, listener: UListener, options: CallOptions = CallOptions.DEFAULT
    ) -> UStatus:
        await self.__subscription_client.unsubscribe(topic, listener, options)

    async def fetch_subscribers(
        self, topic: UUri, options: Optional[CallOptions] = CallOptions.DEFAULT
    ) -> FetchSubscribersResponse:
        await self.__subscription_client.fetch_subscribers(topic, options)

    async def fetch_subscriptions(
        self, request: FetchSubscriptionsRequest, options: Optional[CallOptions] = CallOptions.DEFAULT
    ) -> FetchSubscriptionsResponse:
        await self.__subscription_client.fetch_subscriptions(request, options)

    async def publish(
        self, topic: UUri, options: Optional[CallOptions] = None, payload: Optional[UPayload] = None
    ) -> UStatus:
        return await self.__publisher.publish(topic, options, payload)

    async def register_request_handler(self, method_uri: UUri, handler):
        return await self.__rpc_server.register_request_handler(method_uri, handler)

    async def unregister_request_handler(self, method_uri: UUri, handler):
        return await self.__rpc_server.unregister_request_handler(method_uri, handler)

    async def invoke_method(
        self, method_uri: UUri, request_payload: UPayload, options: Optional[CallOptions] = None
    ) -> UPayload:
        return await self.__rpc_client.invoke_method(method_uri, request_payload, options)

    async def register_listener(
        self, source_filter: UUri, listener: UListener, sink_filter: UUri = UriFactory.ANY
    ) -> UStatus:
        return await self.__transport.register_listener(source_filter, listener, sink_filter)
