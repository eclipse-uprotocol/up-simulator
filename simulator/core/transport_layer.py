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

from concurrent.futures import Future

from uprotocol.proto.uattributes_pb2 import UAttributes
from uprotocol.proto.upayload_pb2 import UPayload
from uprotocol.proto.uri_pb2 import UEntity
from uprotocol.proto.uri_pb2 import UUri
from uprotocol.proto.ustatus_pb2 import UStatus
from uprotocol.transport.ulistener import UListener
from uprotocol_zenoh.zenoh_utransport import Zenoh

utransport = "ZENOH"
ZENOH_IP = '10.0.0.33'
ZENOH_PORT =9090


class TransportLayer:
    ZENOH = Zenoh(ZENOH_IP, ZENOH_PORT)

    def __init__(self):
        if utransport == "ZENOH":
            self.instance = self.ZENOH
        else:
            raise ValueError("Unimplemented")

    def invoke_method(self, topic: UUri, payload: UPayload, attributes: UAttributes) -> Future:
        return self.instance.invoke_method(topic, payload, attributes)

    def authenticate(self, u_entity: UEntity) -> UStatus:
        return self.instance.authenticate(u_entity)

    def send(self, topic: UUri, payload: UPayload, attributes: UAttributes) -> UStatus:
        return self.instance.send(topic, payload, attributes)

    def register_listener(self, topic: UUri, listener: UListener) -> UStatus:
        return self.instance.register_listener(topic, listener)

    def unregister_listener(self, topic: UUri, listener: UListener) -> UStatus:
        return self.instance.unregister_listener(topic, listener)


if __name__ == "__main__":
    TransportLayer().authenticate(UEntity.EMPTY)
