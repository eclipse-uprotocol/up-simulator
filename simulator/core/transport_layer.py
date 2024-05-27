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
import os
import pathlib
from concurrent.futures import Future
from typing import List

from uprotocol.proto.uattributes_pb2 import CallOptions
from uprotocol.proto.umessage_pb2 import UMessage
from uprotocol.proto.upayload_pb2 import UPayload
from uprotocol.proto.uri_pb2 import UAuthority, UEntity, UUri
from uprotocol.proto.ustatus_pb2 import UStatus
from uprotocol.transport.ulistener import UListener

from simulator.core import vehicle_service_utils

try:
    from uprotocol_vsomeip.vsomeip_utransport import (
        VsomeipTransport,
        VsomeipHelper,
    )
except ImportError:
    pass

from simulator.core.binder_utransport import AndroidBinder
from simulator.utils.constant import RESOURCE_CATALOG_JSON_NAME


class Helper(VsomeipHelper):

    def services_info(self) -> List[VsomeipHelper.UEntityInfo]:
        entity_info = []
        cwd = pathlib.Path(__file__).parent.resolve()
        # Specify the relative path to the CSV file
        relative_path = os.path.abspath(os.path.join(cwd, "../target/resource_catalog"))
        # Combine the current working directory and the relative path
        json_file_path = relative_path + os.sep + RESOURCE_CATALOG_JSON_NAME
        with open(json_file_path, "r") as json_file:
            json_data = json_file.read()
            resource_catalog = json.loads(json_data)
            port = 30509
            for data in resource_catalog["node"]:
                # Extract service id, name, and topic ids
                topic_ids = []
                if (
                    "node" in data
                    and "id" in data["node"]
                    and "type" in data["node"]
                    and data["node"]["type"] == "service"
                ):
                    service_name = data["node"]["uri"].split("/")[1]

                    service_id = data["node"]["id"]
                    for node in data["node"]["node"]:
                        if "type" in node and node["type"] == "topic":
                            topic_ids.append(int(node["id"]))
                    for property in data["node"]["properties"]:
                        if property["name"] == "version_major":
                            major_version = property["value"]
                            break
                    if service_name in vehicle_service_utils.someip_entity:
                        entity_info.append(
                            VsomeipHelper.UEntityInfo(
                                Name=service_name,
                                Id=int(service_id),
                                Events=topic_ids,
                                Port=port,
                                MajorVersion=major_version,
                            )
                        )
                    port = port + 1
        return entity_info


class TransportLayer:
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
            self.__instance = None
            self.__ZENOH_IP = "10.0.3.3"
            self.__ZENOH_PORT = 9090
            self.__utransport = "BINDER"
            self._update_instance()

    def set_transport(self, transport: str):
        if self.__utransport != transport:
            print(
                "set transport, previous is",
                self.__utransport,
                "current is",
                transport,
            )
            self.__utransport = transport
            self._update_instance()

    def get_transport(self):
        return self.__utransport

    def set_zenoh_config(self, ip, port):
        if self.__ZENOH_PORT != port or self.__ZENOH_IP != ip:
            self.__ZENOH_PORT = port
            self.__ZENOH_IP = ip
            self._update_instance()

    def set_someip_config(self, localip, multicast):
        self.__utransport = "SOME/IP"
        self._update_instance()

    def _update_instance(self):
        if self.__utransport == "BINDER":
            self.__instance = AndroidBinder()
        elif self.__utransport == "ZENOH":
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
            
            self.__instance = UPClientZenoh(
                conf, UAuthority(name="test_authority"), UEntity(name="test_entity", version_major=1)
            )

        elif self.__utransport == "SOME/IP":
            self.__helper = VsomeipHelper()
            self.__instance = VsomeipTransport(helper=Helper())

    def invoke_method(
        self, topic: UUri, payload: UPayload, calloptions: CallOptions
    ) -> Future:
        return self.__instance.invoke_method(topic, payload, calloptions)

    def send(self, umessage: UMessage) -> UStatus:
        return self.__instance.send(umessage)

    def register_listener(self, topic: UUri, listener: UListener) -> UStatus:
        return self.__instance.register_listener(topic, listener)

    def unregister_listener(self, topic: UUri, listener: UListener) -> UStatus:
        return self.__instance.unregister_listener(topic, listener)

    def start_service(self, entity) -> bool:
        if self.__utransport == "BINDER":
            return self.__instance.start_service(entity)
        else:
            return True

    def create_topic(self, entity, topics, listener):
        if self.__utransport == "BINDER":
            return self.__instance.create_topic(entity, topics, listener)
        else:
            return True
