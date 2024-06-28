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

from uprotocol.proto.uri_pb2 import UAuthority, UEntity, UUri

try:
    from uprotocol_vsomeip.vsomeip_utransport import (
        VsomeipHelper,
        VsomeipTransport,
    )

    from tdk.transport.someip_helper import SomeipHelper
except ImportError:
    pass

from uprotocol.uri.factory.uresource_builder import UResourceBuilder

from tdk.transport.socket_utransport import SocketTransport


class TransportConfiguration:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            # Initialize the singleton instance
            self._initialized = True
            self.ut_instance = None
            self.__ZENOH_IP = "10.0.3.3"
            self.__ZENOH_PORT = 9090
            self.__SOMEIP_UNICAST_IP = "127.0.0.1"
            self.__SOMEIP_MULTICAST_IP = "224.224.224.245"
            self.utransport = "SOCKET"
            self._update_instance()

    def set_transport(self, transport: str):
        if self.utransport != transport:
            print(
                "set transport, previous is",
                self.utransport,
                "current is",
                transport,
            )
            self.utransport = transport
            self._update_instance()

    def get_transport(self):
        return self.utransport

    def set_zenoh_config(self, ip, port):
        self.utransport = "ZENOH"
        if self.__ZENOH_PORT != port or self.__ZENOH_IP != ip:
            self.__ZENOH_PORT = port
            self.__ZENOH_IP = ip
            self._update_instance()

    def set_someip_config(self, localip, multicast):
        self.utransport = "SOME/IP"
        self.__SOMEIP_UNICAST_IP = localip
        self.__SOMEIP_MULTICAST_IP = multicast
        self._update_instance()

    def _update_instance(self):
        if self.utransport == "SOCKET":
            self.ut_instance = SocketTransport()
        elif self.utransport == "ZENOH":
            import zenoh

            zenoh_ip = self.__ZENOH_IP
            zenoh_port = self.__ZENOH_PORT
            conf = zenoh.Config()
            if zenoh_ip is not None:
                endpoint = [f"tcp/{zenoh_ip}:{zenoh_port}"]
                print(f"EEE: {endpoint}")
                conf.insert_json5(zenoh.config.MODE_KEY, json.dumps("client"))
                conf.insert_json5(zenoh.config.CONNECT_KEY, json.dumps(endpoint))
            from up_client_zenoh.upclientzenoh import UPClientZenoh

            self.ut_instance = UPClientZenoh(
                conf, UAuthority(name="simulator_authority"), UEntity(name="simulator_entity", version_major=1)
            )

        elif self.utransport == "SOME/IP":
            self.__helper = VsomeipHelper()
            self.ut_instance = VsomeipTransport(
                helper=SomeipHelper(),
                source=UUri(
                    authority=UAuthority(name="simulator_authority"),
                    entity=UEntity(name="simulator_entity", version_major=1),
                    resource=UResourceBuilder.for_rpc_response(),
                ),
                unicast=self.__SOMEIP_UNICAST_IP,
                multicast=(self.__SOMEIP_MULTICAST_IP, 30490),
            )
