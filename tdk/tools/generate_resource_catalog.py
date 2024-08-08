"""
SPDX-FileCopyrightText: 2024 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
"""

import csv
import importlib
import json
import os
import pkgutil

from google._upb._message import RepeatedCompositeContainer

from tdk.target import protofiles as proto
from tdk.utils.constant import (
    KEY_URI_PREFIX,
    RESOURCE_CATALOG_CSV_NAME,
    RESOURCE_CATALOG_DIR,
    RESOURCE_CATALOG_JSON_NAME,
)

topic_list = []


def create_service_json(service_name, version, service_id, properties):
    json_structure = {
        "uri": f"{KEY_URI_PREFIX}/{service_name}/{version}",
        "uri_id": f"{KEY_URI_PREFIX}/{service_id}/{version}",
        "id": f"{service_id}",
        "type": "service",
    }
    if properties:
        json_structure["properties"] = properties
    return json_structure


def create_method_json(service_uri, service_uri_id, method_name, method_id):
    json_structure = {
        "uri": f"{service_uri}/rpc.{method_name}",
        "uri_id": f"{service_uri_id}/{method_id}",
        "id": f"{method_id}",
        "type": "method",
    }
    return json_structure


def create_topic_json(service_uri, service_uri_id, resource_name, message, topic_id, full_name):
    json_structure = {
        "uri": f"{service_uri}/{resource_name}#{message}",
        "uri_id": f"{service_uri_id}/{topic_id}",
        "id": f"{topic_id}",
        "type": "topic",
    }
    topic_list.append({"uri": json_structure["uri"], "package": full_name})

    return json_structure


def get_package_name(full_name):
    # Find the last dot in the fully qualified name
    last_dot_index = full_name.rfind('.')
    if last_dot_index == -1:
        # No dot found, return the whole name (or handle as needed)
        return ''
    # Return the substring up to and including the last dot
    return full_name[: last_dot_index + 1]


def get_protobuf_descriptor_data():
    node_json = []
    method_nodes = []
    for importer, modname, ispkg in pkgutil.walk_packages(
        path=proto.__path__, prefix=proto.__name__ + ".", onerror=lambda x: print(f"Error parsing {x}")
    ):
        if not modname.endswith("__pycache__"):
            mod = importlib.import_module(modname)

            try:
                _services = mod.DESCRIPTOR.services_by_name.keys()
            except Exception:
                continue

            for service in _services:
                service_json = {"node": {}}
                message_options_dict = []
                message_resource_prefix_dict = []
                service_descriptor = mod.DESCRIPTOR.services_by_name[service]
                options = service_descriptor.GetOptions()
                properties = []
                for field, value in options.ListFields():
                    if field.name in ["service_id", "id"]:
                        service_id = value
                    elif field.name in ["service_name", "name"]:
                        service_name = value
                    else:
                        if field.name in ["service_version_major", "version_major"]:
                            version = value
                        if isinstance(value, RepeatedCompositeContainer):
                            continue
                        properties.append({"name": field.name, "value": value})
                service_json["node"] = create_service_json(service_name, version, service_id, properties)

                method_nodes = []
                for method in service_descriptor.methods_by_name.keys():
                    # get method object
                    options = service_descriptor.methods_by_name[method].GetOptions()
                    for field, value in options.ListFields():
                        if field.name == "method_id":
                            method_id = value
                            method_nodes.append(
                                create_method_json(
                                    f"{KEY_URI_PREFIX}/{service_name}/{version}",
                                    service_json["node"]["uri_id"],
                                    method,
                                    method_id,
                                )
                            )
                message_option_descriptor = mod.DESCRIPTOR.message_types_by_name
                for message in message_option_descriptor.keys():
                    if "Options" in message:
                        for key in ["resource_name", "name"]:
                            if key in message_option_descriptor[message].fields_by_name.keys():
                                for field, value in (
                                    message_option_descriptor[message].fields_by_name[key].GetOptions().ListFields()
                                ):
                                    if "resource_name_mask" == field.name:
                                        resource_name_mask_value = value.rstrip(".*")
                                        if len(resource_name_mask_value) > 0:
                                            message_resource_prefix_dict.append(
                                                {f"{message.replace('Options', '')}": resource_name_mask_value}
                                            )
                                        break
                            for field, value in message_option_descriptor[message].GetOptions().ListFields():
                                if field.name == "base_topic_id":
                                    message_options_dict.append({f"{message.replace('Options', '')}": value})
                                    break

                service_json["node"]["node"] = method_nodes

            try:
                if service_json["node"] != {}:
                    topic_nodes = []
                    package_name = get_package_name(service_descriptor.full_name)
                    for field, value in service_descriptor.GetOptions().ListFields():
                        if field.name == "publish_topic":
                            for uservice_topic in value:
                                topic_id = uservice_topic.id
                                resource_name = uservice_topic.name
                                message = uservice_topic.message
                                # TODO: remove after BrakeAssistance message available in proto
                                if message in [
                                    "BrakeAssistance",
                                    "ObjectDataGroup",
                                    "FunctionalStatus",
                                    "ObjectDataGroup",
                                    "FunctionalStatus",
                                    "RadarDetectionDataHeader",
                                ]:
                                    continue
                                topic_nodes.append(
                                    create_topic_json(
                                        f"{KEY_URI_PREFIX}/{service_name}/{version}",
                                        service_json["node"]["uri_id"],
                                        resource_name,
                                        message,
                                        topic_id,
                                        full_name=package_name + message,
                                    )
                                )
                    if service_json:
                        if topic_nodes and len(topic_nodes) > 0:
                            service_json["node"]["node"] = service_json["node"]["node"] + topic_nodes
                        node_json.append(service_json)
                        service_json = None
            except Exception:
                continue

    resource_catalog_json = {"node": node_json}
    return resource_catalog_json


def write_topics_to_csv_file():
    csv_file_path = os.path.join(RESOURCE_CATALOG_DIR, RESOURCE_CATALOG_CSV_NAME)
    with open(csv_file_path, "w", newline="") as csv_file:
        csv_writer = csv.writer(csv_file)
        for topic_info in topic_list:
            csv_writer.writerow([topic_info["uri"], topic_info["package"]])
        print("resource_catalog.csv is created successfully")


def write_nodes_to_json_file(resource_catalog_json):
    # Write JSON data to the services.json
    if not os.path.exists(RESOURCE_CATALOG_DIR):
        os.makedirs(RESOURCE_CATALOG_DIR)
    json_file_path = os.path.join(RESOURCE_CATALOG_DIR, RESOURCE_CATALOG_JSON_NAME)
    with open(json_file_path, "w") as json_file:
        json.dump(resource_catalog_json, json_file, indent=2)
        print("resource_catalog.json is created successfully")


def execute():
    write_nodes_to_json_file(get_protobuf_descriptor_data())
    write_topics_to_csv_file()


if __name__ == "__main__":
    execute()
