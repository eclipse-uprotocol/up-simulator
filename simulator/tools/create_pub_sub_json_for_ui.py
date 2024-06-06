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

from google.protobuf.descriptor import FieldDescriptor

from simulator.core import protobuf_autoloader as autoloader
from simulator.tools.common_methods import (
    check_for_recursive_declaration,
    get_config_name,
    get_field_info,
    get_max,
    get_min_value,
    get_property_text,
    get_type_in_string,
)
from simulator.utils import constant

result_data = {}
additional_data = {}
services = list(autoloader.get_services())


def get_config_display_name(name):
    return name.rsplit(".", 1)[-1]


def get_pubsub(service_name):
    output = set()
    for item in autoloader.get_topics_by_proto_service_name(service_name):
        status = item.split("#")[-1]
        output.add(status)
    return list(output)


def get_topics_by_resource_name(resource_name, service_name):
    topics = autoloader.get_topics_by_proto_service_name(service_name)
    return [topic for topic in topics if topic.lower().split("#")[1] == resource_name.lower()]


def get_pure_class_type(topic):
    return next(
        (pair[1] for pair in autoloader.topic_messages if topic == pair[0]),
        None,
    )


def get_ui_details(topic):
    all_field_info = {}
    class_type = get_pure_class_type(topic)
    message_class = autoloader.find_message(class_type)
    field_info = {}
    for field_descriptor in message_class.DESCRIPTOR.fields:
        if not (
            field_descriptor.type == FieldDescriptor.TYPE_ENUM
            and field_descriptor.enum_type.name in ["Resource", "Resources"]
        ) and not check_for_recursive_declaration(field_descriptor):
            field_info[field_descriptor.name] = get_field_info(field_descriptor)
    message_name = message_class.DESCRIPTOR.name
    all_field_info[message_name] = field_info
    return all_field_info


def remove_key_prefix(json_data, prefix):
    if isinstance(json_data, dict):
        for key, value in list(json_data.items()):  # Use list() to avoid modifying the dictionary while iterating
            if key == "property" and value.startswith(prefix):
                # Remove the key prefix
                value = value[len(prefix) :]
                json_data[key] = value
                property_text_key = key + "Text"
                if property_text_key in json_data and json_data[property_text_key] == value:
                    del json_data[property_text_key]  # Remove propertyText key if its value is the same as property
            elif isinstance(value, (dict, list)):
                remove_key_prefix(value, prefix)
    elif isinstance(json_data, list):
        for item in json_data:
            if "key" in item:
                new_prefix = item.get("key") + "."
                item["key"] = item["key"][len(prefix) :]
                remove_key_prefix(item, new_prefix)
            remove_key_prefix(item, prefix)


def extract_fields(data):
    result = []
    unique_ui = []
    check = False
    for key, value in data.items():
        if isinstance(value, dict):
            if (
                "type_field" in value
                and value["type_field"]
                not in [
                    FieldDescriptor.TYPE_MESSAGE,
                    FieldDescriptor.TYPE_ENUM,
                ]
                and value.get("label") == "Non-repeated"
            ):
                type_str = get_type_in_string(value["type_field"])
                property_value = value["property"]
                result_dict = {"type": type_str, "property": property_value}
                if type_str in {"int", "float", "double"}:
                    result_dict.update(
                        {
                            "minrange": get_min_value(property_value),
                            "maxrange": get_max(property_value),
                        }
                    )
                if "." in property_value:
                    property_text = get_property_text(property_value)
                    if property_value != property_text:
                        result_dict["propertyText"] = property_text

                result.append(result_dict)

            elif (
                "type_field" in value
                and value["type_field"] == FieldDescriptor.TYPE_ENUM
                and value.get("label") == "Non-repeated"
            ):
                property_value = value["property"]
                result_dict = {
                    "type": "dropdown",
                    "property": property_value,
                    "mode": value["enum_values"],
                }
                if "." in property_value:
                    property_text = get_property_text(property_value)
                    if property_value != property_text:
                        result_dict["propertyText"] = property_text

                result.append(result_dict)

            elif (
                "type_field" in value
                and value["type_field"] == FieldDescriptor.TYPE_MESSAGE
                and value.get("label") == "Non-repeated"
            ):
                result.append({"type": "label", "text": value["message_name"]})
            elif (
                "type_field" in value
                and value["type_field"] == FieldDescriptor.TYPE_MESSAGE
                and value.get("label") == "Repeated"
            ):
                check = True
                key = value["property"]
                repeated_value_dict = extract_fields(value)
                remove_key_prefix(repeated_value_dict, key + ".")
                result.append(
                    {
                        "type": "repeated",
                        "class": value["message_name"],
                        "key": key,
                        "value": repeated_value_dict,
                    }
                )

            elif (
                "type_field" in value
                and value["type_field"] != FieldDescriptor.TYPE_MESSAGE
                and value.get("label") == "Repeated"
            ):
                type_str = get_type_in_string(value["type_field"])
                if type_str in {"int", "float", "double"}:
                    result.append(
                        {
                            "type": "repeated",
                            "class": type_str,
                            "key": value["property"],
                            "value": [
                                {
                                    "type": type_str,
                                    "property": value["property"],
                                    "minrange": get_min_value(value["property"]),
                                    "maxrange": get_max(value["property"]),
                                }
                            ],
                        }
                    )
                if type_str == "string" or type_str == "bool":
                    result.append(
                        {
                            "type": "repeated",
                            "class": type_str,
                            "key": value["property"],
                            "value": [
                                {
                                    "type": type_str,
                                    "property": value["property"],
                                }
                            ],
                        }
                    )

                if (
                    "type_field" in value
                    and value["type_field"] == FieldDescriptor.TYPE_ENUM
                    and "label" in value
                    and value["label"] == "Repeated"
                ):
                    result.append(
                        {
                            "type": "repeated",
                            "class": value["enum_name"],
                            "key": value["property"],
                            "value": [
                                {
                                    "type": "dropdown",
                                    "property": value["property"],
                                    "mode": value["enum_values"],
                                },
                            ],
                        }
                    )

            if check:
                check = False
            else:
                result.extend(extract_fields(value))

    seen_labels = set()
    for item in result:
        if item["type"] != "Label" or tuple(item.items()) not in seen_labels:
            unique_ui.append(item)
            if item["type"] == "Label":
                seen_labels.add(tuple(item.items()))

    return unique_ui


def get_ui(pubsub, service_name):
    ui_item = []
    if service_name not in [
        "core.utelemetry",
        "core.usubscription",
        "core.udiscovery",
    ]:
        for resource_name in pubsub:
            topics = get_topics_by_resource_name(resource_name, service_name)
            if len(topics) > 0:
                configuration = []
                for i in range(len(topics)):
                    name = get_config_name(topics[i])
                    display_name = get_config_display_name(name)
                    if name == display_name:
                        configuration_dict = {"name": name, "topic": topics[i]}
                    else:
                        configuration_dict = {
                            "name": name,
                            "display_name": display_name,
                            "topic": topics[i],
                        }
                    configuration.append(configuration_dict)
                ui_det = get_ui_details(configuration[0]["topic"])
                ui_details = extract_fields(ui_det)
                if not ui_details:
                    ui_details = [{"type": "label", "text": "No protofields available"}]

                modified_ui_list = ui_details
                if "Geofence" not in resource_name:
                    modified_ui_list = [
                        item
                        for item in ui_details
                        if not (item.get("type") == "string" and item.get("property") == "name")
                    ]

                part_dict = {
                    resource_name: {
                        "Configuration": configuration,
                        "uidetails": modified_ui_list,
                    }
                }
                ui_item.append(part_dict)
    return ui_item


def check_resource(message):
    topic = message[0]["topic"]
    class_type = get_pure_class_type(topic)
    message_class = autoloader.find_message(class_type)
    field_names = message_class.DESCRIPTOR.fields_by_name.keys()
    for field_name in field_names:
        field_descriptor = message_class.DESCRIPTOR.fields_by_name[field_name]
        if field_descriptor.type == FieldDescriptor.TYPE_ENUM and field_descriptor.enum_type.name in [
            "Resource",
            "Resources",
        ]:
            return field_name
    return None


def execute():
    # Process services
    for service in services:
        data = get_ui(get_pubsub(service), service)
        if len(data) > 0:
            result_data[service] = data

    # Validate and modify configuration
    for service_dict in result_data.values():
        for val in service_dict:
            config_key = list(val.keys())[0]
            validate = check_resource(val[config_key]["Configuration"])
            if validate is not None:
                for component in val[config_key]["Configuration"]:
                    component["name_key"] = validate

    # Create the directory if it doesn't exist
    if not os.path.exists(constant.UI_JSON_DIR):
        os.makedirs(constant.UI_JSON_DIR)
    pub_sub_json_file_path = os.path.join(constant.UI_JSON_DIR, constant.PUB_SUB_JSON_FILE_NAME)
    # Write JSON data to the pub-sub.json
    with open(pub_sub_json_file_path, "w") as json_file:
        json.dump(result_data, json_file, indent=2)
        print("pub-sub.json is created successfully")


if __name__ == "__main__":
    execute()
