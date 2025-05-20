"""
SPDX-FileCopyrightText: 2024 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

import json

from up_transport_zenoh.uptransportzenoh import UPTransportZenoh
from uprotocol.transport.utransport import UTransport
from uprotocol.v1.uri_pb2 import UUri

from tdk.helper.binder_utransport import SocketTransport

try:
    from uprotocol_vsomeip.vsomeip_utransport import (
        VsomeipTransport,
    )

    from tdk.helper.someip_helper import SomeipHelper
except ImportError:
    pass


class TransportConfiguration:
    def __init__(self):
        self.__SOURCE = UUri(authority_name="tdk", ue_id=99998, ue_version_major=1)
        self.__ZENOH_IP = "10.0.0.33"
        self.__ZENOH_PORT = 9090
        self.__SOMEIP_UNICAST_IP = "127.0.0.1"
        self.__SOMEIP_MULTICAST_IP = "224.224.224.245"
        self.__transport = self._update_instance("SOME/IP")

    def _update_instance(self, transport_name="BINDER") -> UTransport:
        if transport_name == "BINDER":
            return SocketTransport(self.__SOURCE)
        elif transport_name == "ZENOH":
            import zenoh

            conf = zenoh.Config()
            if self.__ZENOH_IP is not None:
                endpoint = [f"tcp/{self.__ZENOH_IP}:{self.__ZENOH_PORT}"]
                print(f"endpoint: {endpoint}")
                conf.insert_json5(zenoh.config.MODE_KEY, json.dumps("client"))
                conf.insert_json5(zenoh.config.CONNECT_KEY, json.dumps(endpoint))

            return UPTransportZenoh.new(conf, self.__SOURCE)
        elif transport_name == "SOME/IP":
            return VsomeipTransport(
                source=self.__SOURCE,unicast=self.__SOMEIP_UNICAST_IP, multicast=(self.__SOMEIP_MULTICAST_IP, 30490), helper=SomeipHelper()
            )

    def get_transport(self) -> UTransport:
        return self.__transport

    def get_transport_env(self) -> str:
        if isinstance(self.__transport, UPTransportZenoh):
            return "ZENOH"
        try:
            if isinstance(self.__transport, VsomeipTransport):
                return "SOME/IP"
        except Exception:
            pass

        return "BINDER"

    def set_zenoh_config(self, ip, port):
        self.__ZENOH_PORT = port
        self.__ZENOH_IP = ip
        self.__transport = self._update_instance("ZENOH")

    def set_someip_config(self, localip, multicast):
        self.__SOMEIP_UNICAST_IP = localip
        self.__SOMEIP_MULTICAST_IP = multicast
        self.__transport = self._update_instance("SOME/IP")

    def set_transport(self, env):
        if self.get_transport_env() != env:
            print(f"previously selected transport is {self.get_transport_env()} and now is {env}")
            if env == "SOME/IP":
                self.set_someip_config(self.__SOMEIP_UNICAST_IP, self.__SOMEIP_MULTICAST_IP)
            elif env == "ZENOH":
                self.set_zenoh_config(self.__ZENOH_IP, self.__ZENOH_PORT)
            else:
                self.__transport = self._update_instance("BINDER")

    def start_service(self, entity) -> bool:
        if self.get_transport_env() == "BINDER":
            return self.start_service(entity)
        else:
            return True

    def create_topic(self, entity, topics, listener):
        if self.get_transport_env() == "BINDER":
            return self.create_topic(entity, topics, listener)
        else:
            return True
