# -------------------------------------------------------------------------
#
# Copyright (c) 2024 General Motors GTO LLC
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
# SPDX-FileCopyrightText: 2024 General Motors GTO LLC
# SPDX-License-Identifier: Apache-2.0
#
# -------------------------------------------------------------------------

import json
from simulator.core import protobuf_autoloader as autoloader
import os
import simulator.utils.constant as CONSTANTS
from simulator.tools.common_methods import get_field_info, get_max, get_min_value, get_property_text, get_type_in_string

result_data = {}
additional_data = {}
services = list(autoloader.get_services())


def get_resources(service_name):
    resources = []
    try:
        rpcs = autoloader.get_methods_by_service(service_name).keys()
        for rpc in rpcs:
            resources.append(rpc)
        return resources
    except:
        resources = []
        return resources


def find_enum_values(enum_descriptor):
    return [value.name for value in enum_descriptor.values]


def get_enums_without_fields(message_class):
    try:
        enum_values = message_class.DESCRIPTOR.enum_types_by_name.get("Resources", None)
        if enum_values is None:
            enum_values = message_class.DESCRIPTOR.enum_types_by_name.get("Resource", None)
        if enum_values:
            return [enum_value.name for enum_value in enum_values.values]
    except KeyError:
        pass


def get_resources_from_message_class(message_class):
    nested_enum_names = []
    if get_enums_without_fields(message_class) is not None:
        nested_enum_names.extend(get_enums_without_fields(message_class))
    for field_name in message_class.DESCRIPTOR.fields_by_name.keys():
        field_descriptor = message_class.DESCRIPTOR.fields_by_name[field_name]
        if field_descriptor.enum_type is not None and field_descriptor.enum_type.containing_type is not None:
            nested_message_class = autoloader.find_message(field_descriptor.enum_type.containing_type.full_name)
            if get_enums_without_fields(nested_message_class) is not None:
                nested_enum_names.extend(get_enums_without_fields(nested_message_class))

        if field_descriptor.type == 11:  # Assuming type 11 corresponds to a nested message
            nested_message_class = field_descriptor.message_type._concrete_class
            if get_enums_without_fields(nested_message_class) is not None:
                nested_enum_names.extend(get_enums_without_fields(nested_message_class))

    return nested_enum_names


def find_enum_fields_recursive(message_class):
    # This function searched for all the enum fields with message na,e Resource or Resources
    enum_fields = []
    for field_name in message_class.DESCRIPTOR.fields_by_name.keys():
        field_descriptor = message_class.DESCRIPTOR.fields_by_name[field_name]
        if field_descriptor.enum_type is not None and field_descriptor.enum_type.name in ["Resource", "Resources"]:
            enum_values = find_enum_values(field_descriptor.enum_type)
            enum_fields.append({"field_name": field_name, "enum_values": enum_values})
        elif field_descriptor.type == 11:  # 11 corresponds to FieldDescriptor.TYPE_MESSAGE
            nested_message_class = field_descriptor.message_type._concrete_class
            nested_enum_fields = find_enum_fields_recursive(nested_message_class)
            if nested_enum_fields:
                for nested_enum_field in nested_enum_fields:
                    nested_field_name = f"{field_name}.{nested_enum_field['field_name']}"
                    enum_fields.append(
                        {"field_name": nested_field_name, "enum_values": nested_enum_field["enum_values"]})

        return enum_fields


def get_ui_details(resource_name, service_name):
    all_field_info = {}
    try:
        message_class = autoloader.get_request_class(service_name, resource_name)
        field_names = message_class.DESCRIPTOR.fields_by_name.keys()
        field_info = {}
        for field_name in field_names:
            if field_name == "update_mask":
                pass
            else:
                field_descriptor = message_class.DESCRIPTOR.fields_by_name[field_name]
                if field_descriptor.type == 14 and (
                        field_descriptor.enum_type.name == "Resource" or field_descriptor.enum_type.name ==
                        "Resources"):
                    pass
                else:
                    field_info[field_name] = get_field_info(field_descriptor)
        message_name = message_class.DESCRIPTOR.name
        all_field_info[message_name] = field_info
        return all_field_info
    except:
        print(service_name)
        return {}


def remove_key_prefix(json_data, prefix):
    if isinstance(json_data, dict):
        for key, value in list(json_data.items()):  # Use list() to avoid modifying the dictionary while iterating
            if key == "property":
                del json_data['property']
            elif key == "rpcproperty" and value.startswith(prefix):
                # Remove the key prefix
                value = value[len(prefix):]
                json_data[key] = value

            elif isinstance(value, (dict, list)):
                remove_key_prefix(value, prefix)
    elif isinstance(json_data, list):
        for item in json_data:
            if 'key' in item:
                new_prefix = item.get('key') + "."
                item['key'] = item['key'][len(prefix):]
                remove_key_prefix(item, new_prefix)
            remove_key_prefix(item, prefix)


def extract_fields(data):
    result = []
    unique_ui = []
    check = False
    for key, value in data.items():
        if isinstance(value, dict):
            if 'type_field' in value and value['type_field'] not in [11, 14] and value.get('label') == 'Non-repeated':
                type_str = get_type_in_string(value['type_field'])
                property_value = value['property']
                result_dict = {'type': type_str, 'property': property_value}
                if type_str in {'int', 'float', 'double'}:
                    result_dict.update({'minrange': get_min_value(property_value), 'maxrange': get_max(property_value)})
                if '.' in property_value:
                    property_text = get_property_text(property_value)
                    if property_value != property_text:
                        result_dict['property'] = property_text
                        result_dict['rpcproperty'] = property_value

                result.append(result_dict)

            elif 'type_field' in value and value['type_field'] == 14 and value.get('label') == 'Non-repeated':
                property_value = value['property']
                result_dict = {'type': 'dropdown', 'property': property_value, 'mode': value['enum_values']}
                if '.' in property_value:
                    property_text = get_property_text(property_value)
                    if property_value != property_text:
                        result_dict['property'] = property_text
                        result_dict['rpcproperty'] = property_value

                result.append(result_dict)

            elif 'type_field' in value and value['type_field'] == 11 and value.get('label') == 'Non-repeated':
                result.append({'type': 'label', 'text': value['message_name']})
            elif 'type_field' in value and value['type_field'] == 11 and value.get('label') == "Repeated":
                check = True
                key = value['property']
                repeated_value_dict = extract_fields(value)
                remove_key_prefix(repeated_value_dict, key + ".")
                result.append(
                    {'type': 'repeated', 'class': value['message_name'], 'key': key, 'value': repeated_value_dict})

            elif 'type_field' in value and value['type_field'] != 11 and value.get('label') == 'Repeated':
                type_str = get_type_in_string(value['type_field'])
                if type_str in {'int', 'float', 'double'}:
                    result.append({'type': 'repeated', 'class': type_str, 'key': value['property'], 'value': [
                        {'type': type_str, 'property': value["property"], 'minrange': get_min_value(value['property']),
                         'maxrange': get_max(value['property'])}]})
                if type_str == 'string' or type_str == 'bool':
                    result.append({'type': 'repeated', 'class': type_str, 'key': value['property'],
                                   'value': [{'type': type_str, 'property': value["property"]}]})

                if 'type_field' in value and value['type_field'] == 14 and 'label' in value and value[
                    'label'] == 'Repeated':
                    result.append({'type': 'repeated', 'class': value["enum_name"], 'key': value['property'], 'value': [
                        {'type': 'dropdown', 'property': value['property'], 'mode': value['enum_values']}, ]})
            if check:

                check = False
            else:
                result.extend(extract_fields(value))

    seen_labels = set()
    for item in result:
        if item['type'] != 'Label' or tuple(item.items()) not in seen_labels:
            unique_ui.append(item)
            if item['type'] == 'Label':
                seen_labels.add(tuple(item.items()))

    return unique_ui


def get_ui(resources, service_name):
    ui_item = []
    for resource_name in resources:
        name = "N"
        display_name = resource_name
        rpc_method = resource_name
        message_class = autoloader.get_request_class(service_name, resource_name)
        configuration = []
        enum_fields = find_enum_fields_recursive(message_class)
        if enum_fields == [] or enum_fields is None:
            enums = get_resources_from_message_class(message_class)
            if enums == [] or enums is None:
                configuration_dict = {"name": name, "display_name": display_name, "rpcmethod": rpc_method}
                configuration.append((configuration_dict))
            else:
                for enum in enums:
                    configuration.append({'name': enum, 'display_name': enum, 'rpcmethod': rpc_method})


        else:
            for enum_field in enum_fields:
                field_name = enum_field['field_name']
                enum_values = enum_field['enum_values']
                for value in enum_values:
                    configuration.append(({"name": value, "name_key": field_name, "rpcmethod": rpc_method}))
        ui_det = get_ui_details(resource_name, service_name)
        if ui_det == {rpc_method: {}}:
            ui_details = [{"type": "label", "text": "Type of RPC request is google.protobuf.Empty"}]
        else:
            ui_details = extract_fields(ui_det)

        if not ui_details:
            ui_details = [{"type": "label", "text": "Type of RPC request is google.protobuf.Empty"}]
        modified_ui_list = ui_details
        # if 'Geofence' not in resource_name:
        #     modified_ui_list = [item for item in ui_details if
        #                         not (item.get('type') == 'string' and item.get('property') == 'name')]
        part_dict = {resource_name: {'Configuration': configuration, 'uidetails': modified_ui_list}}
        ui_item.append(part_dict)

    return ui_item


def execute():
    for service in services:
        data = get_ui(get_resources(service), service)
        if len(data) > 0:
            result_data[service] = data

        # Create the directory if it doesn't exist
    if not os.path.exists(CONSTANTS.UI_JSON_DIR):
        os.makedirs(CONSTANTS.UI_JSON_DIR)
    RPC_JSON_FILE_PATH = os.path.join(CONSTANTS.UI_JSON_DIR, CONSTANTS.RPC_JSON_FILE_NAME)
    # Write JSON data to the pub-sub.json
    with open(RPC_JSON_FILE_PATH, 'w') as json_file:
        json.dump(result_data, json_file, indent=2)
        print("rpc.json is created successfully")


if __name__ == "__main__":
    execute()
