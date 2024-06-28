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
import os
import pathlib
from typing import List

from tdk.utils.constant import RESOURCE_CATALOG_JSON_NAME

try:
    from uprotocol_vsomeip.vsomeip_utransport import (
        VsomeipHelper,
    )
except ImportError:
    pass

someip_entity = []
temp_someip_entity = []


def configure_someip_service(entity_name):
    global temp_someip_entity
    temp_someip_entity.append(entity_name)

class SomeipHelper(VsomeipHelper):
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
                            topic_ids.append(int(node["id"]) + 32768)
                    for property in data["node"]["properties"]:
                        if property["name"] == "version_major":
                            major_version = property["value"]
                            break
                    if service_name in someip_entity:
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
