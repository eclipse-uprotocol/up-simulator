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
# SPDX-FileCopyrightText: 2024   General Motors GTO LLC
# SPDX-License-Identifier: Apache-2.0
#
# -------------------------------------------------------------------------
from google.protobuf.descriptor import FieldDescriptor

from simulator.tools import maxmin_field


def get_enum_info(enum_descriptor, field_descriptor, parent_field_name=""):
    property_name = (
        f"{parent_field_name}.{field_descriptor.name}"
        if parent_field_name
        else field_descriptor.name
    )

    enum_info = {
        "enum_name": enum_descriptor.name,
        "enum_values": [
            {"label": enum_value.name, "value": enum_value.number}
            for enum_value in enum_descriptor.values
        ],
        "property": property_name,
    }
    return enum_info


def get_field_info(field_descriptor, parent_field_name=""):
    field_info = {
        "type_field": field_descriptor.type,
        "label": (
            "Repeated"
            if field_descriptor.label == FieldDescriptor.LABEL_REPEATED
            else "Non-repeated"
        ),
    }

    property_name = (
        f"{parent_field_name}.{field_descriptor.name}"
        if parent_field_name
        else field_descriptor.name
    )
    field_info["property"] = property_name

    if (
        field_descriptor.type == FieldDescriptor.TYPE_MESSAGE
    ):  # If field type is TYPE_MESSAGE
        nested_message_descriptor = field_descriptor.message_type
        field_info["message_name"] = nested_message_descriptor.name
        nested_field_info = {
            nested_field_descriptor.name: get_field_info(
                nested_field_descriptor, field_info["property"]
            )
            for nested_field_descriptor in nested_message_descriptor.fields
            if not (
                nested_field_descriptor.type == FieldDescriptor.TYPE_ENUM
                and nested_field_descriptor.enum_type.name
                in ["Resource", "Resources"]
            )
        }
        field_info.update(nested_field_info)

    if (
        field_descriptor.type == FieldDescriptor.TYPE_ENUM
    ):  # If field type is TYPE_ENUM
        enum_info = get_enum_info(
            field_descriptor.enum_type, field_descriptor, parent_field_name
        )
        field_info.update(enum_info)

    return field_info


def get_config_name(topic):
    return topic.rsplit("/", 1)[-1].rsplit("#", 1)[0]


def get_type_in_string(type_field):
    f = ""
    if type_field == FieldDescriptor.TYPE_FLOAT:
        f = "float"
    if type_field == FieldDescriptor.TYPE_STRING:
        f = "string"
    if type_field in {
        FieldDescriptor.TYPE_INT32,
        FieldDescriptor.TYPE_INT64,
        FieldDescriptor.TYPE_UINT64,
        FieldDescriptor.TYPE_SINT32,
        FieldDescriptor.TYPE_SINT64,
        FieldDescriptor.TYPE_FIXED64,
        FieldDescriptor.TYPE_FIXED32,
        FieldDescriptor.TYPE_UINT32,
        FieldDescriptor.TYPE_SFIXED32,
        FieldDescriptor.TYPE_SFIXED64,
    }:
        f = "int"
    if type_field == FieldDescriptor.TYPE_BOOL:
        f = "bool"
    if type_field == FieldDescriptor.TYPE_ENUM:
        f = "enum"
    if type_field == "message":
        f = "message"
    return f


def get_property_text(input):
    parts = input.split(".", 1)
    if len(parts) > 0:
        return parts[-1]
    else:
        return ""


def check_for_recursive_declaration(
    field_descriptor, field_message_name_hierarchy=""
):
    check = False
    if (
        field_descriptor.type == FieldDescriptor.TYPE_MESSAGE
    ):  # If field type is TYPE_MESSAGE
        nested_message_descriptor = field_descriptor.message_type
        field_message_name_hierarchy = (
            f"{field_message_name_hierarchy}.{nested_message_descriptor.name}"
            if field_message_name_hierarchy
            else nested_message_descriptor.name
        )
        if len(field_message_name_hierarchy.split(".")) == len(
            set(field_message_name_hierarchy.split("."))
        ):
            for nested_field_descriptor in nested_message_descriptor.fields:
                if (
                    nested_field_descriptor.type
                    == nested_field_descriptor.TYPE_MESSAGE
                ):
                    if check_for_recursive_declaration(
                        nested_field_descriptor, field_message_name_hierarchy
                    ):
                        check = True
        else:
            check = True
    return check


def get_max(property):
    for prop, value in maxmin_field.MAX_VALUES.items():
        if prop in property:
            return value
    return maxmin_field.default_max


def get_min_value(property):
    for prop, value in maxmin_field.MIN_VALUES.items():
        if prop in property:
            return value
    return maxmin_field.default_min
