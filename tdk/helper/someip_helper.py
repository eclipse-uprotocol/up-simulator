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
from google.protobuf.descriptor import FieldDescriptor

from tdk.utils.constant import RESOURCE_CATALOG_JSON_NAME
from google.protobuf.message import Message
try:
    from uprotocol_vsomeip.vsomeip_utransport import (
        VsomeipHelper,
    )
except ImportError:
    pass

someip_entity = []
temp_someip_entity = []
is_serializer_enabled=False

def ensure_defaults(message: Message) -> Message:
    """
    Ensures that all fields in a Protobuf message are explicitly set.
    This is required for SOME/IP serialization where no fields should be omitted.

    :param message: Protobuf message object
    :return: Modified message with default values explicitly set
    """
    print("Ensuring defaults for:", message)
    default_message = message.__class__()  # Create a new instance with default values

    for field in message.DESCRIPTOR.fields:
        field_name = field.name
        field_value = getattr(message, field_name, None)

        # ✅ Handle nested Protobuf messages (recursively process)
        if field.type == FieldDescriptor.TYPE_MESSAGE and field_value is not None:
            ensure_defaults(field_value)

        # ✅ Handle fields that do not support HasField() (primitive types like int, string, bool)
        elif field.label != FieldDescriptor.LABEL_REPEATED:  # Not a repeated field
            try:
                if not message.HasField(field_name):  # Only call HasField() if field supports it
                    setattr(message, field_name, getattr(default_message, field_name))  # Assign default
            except ValueError:  # Primitive types (int, float, string) don’t support HasField()
                if field_value in [None, "", 0, False]:  # If unset, assign default
                    setattr(message, field_name, getattr(default_message, field_name))

        # ✅ Handle repeated fields (lists)
        elif field.label == FieldDescriptor.LABEL_REPEATED:
            if not field_value:  # If list is empty, set to default
                setattr(message, field_name, getattr(default_message, field_name))
     #   print(f"Message with all value set: {message}")
    return message  #

def configure_someip_service(entity_name):
    global temp_someip_entity
    temp_someip_entity.append(entity_name)


try:

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
                             if property["name"] == "service_version_major":
                                major_version = property["value"]
                                break
                        if service_name in someip_entity:
                            entity_info.append(
                                VsomeipHelper.UEntityInfo(
                                    service_id=int(service_id),
                                    events=topic_ids,
                                    port=port,
                                    major_version=major_version,
                                )
                            )
                        port = port + 1
            return entity_info
except NameError:
    pass
