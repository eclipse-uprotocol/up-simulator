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
from concurrent.futures import Future

from uprotocol.proto.uattributes_pb2 import CallOptions
from uprotocol.proto.umessage_pb2 import UMessage
from uprotocol.proto.upayload_pb2 import UPayload
from uprotocol.proto.uri_pb2 import UUri
from uprotocol.proto.ustatus_pb2 import UStatus
from uprotocol.transport.ulistener import UListener

from tdk.transport.transport_configuration import TransportConfiguration


class CommunicationLayer:

    def __init__(self, tc: TransportConfiguration):
        self._tc = tc

    def invoke_method(self, topic: UUri, payload: UPayload, calloptions: CallOptions) -> Future:
        return self._tc.ut_instance.invoke_method(topic, payload, calloptions)

    def send(self, umessage: UMessage) -> UStatus:
        return self._tc.ut_instance.send(umessage)

    def register_listener(self, topic: UUri, listener: UListener) -> UStatus:
        return self._tc.ut_instance.register_listener(topic, listener)

    def unregister_listener(self, topic: UUri, listener: UListener) -> UStatus:
        return self._tc.ut_instance.unregister_listener(topic, listener)

    def start_service(self, entity) -> bool:
        if self._tc.utransport == "SOCKET":
            return self._tc.ut_instance.start_service(entity)
        else:
            return True

    def create_topic(self, entity, topics, listener):
        if self._tc.utransport == "SOCKET":
            return self._tc.ut_instance.create_topic(entity, topics, listener)
        else:
            return True
