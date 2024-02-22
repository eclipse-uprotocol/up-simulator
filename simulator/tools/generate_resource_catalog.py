import csv
import importlib
import json
import os
import pkgutil
import re

from simulator.utils.constant import RESOURCE_CATALOG_DIR, RESOURCE_CATALOG_JSON_NAME, RESOURCE_CATALOG_CSV_NAME, \
    PROTO_REPO_DIR, KEY_URI_PREFIX, KEY_PROTO_ENTITY_NAME
from target import protofiles as proto
from google.protobuf import reflection

topic_list = []


def create_service_json(service_name, version, service_id, properties):
    json_structure = {"uri": f"{KEY_URI_PREFIX}:/{service_name}/{version}", "id": f"{service_id}", "type": "service", }
    if properties:
        json_structure["properties"] = properties
    return json_structure


def create_method_json(service_uri, method_name, method_id):
    json_structure = {"uri": f"{service_uri}/rpc.{method_name}", "id": f"{method_id}", "type": "method", }
    return json_structure


def create_topic_json(service_uri, resource, message, topic_id, full_name, message_resource_prefix_dict):
    prefix = next((d[message] for d in message_resource_prefix_dict if message in d), '')
    if len(prefix) > 0:
        prefix = prefix + '.'
    resource = prefix + resource
    json_structure = {"uri": f"{service_uri}/{resource}#{message}", "id": f"{topic_id}", "type": "topic", }
    topic_list.append({"uri": json_structure['uri'], "package": full_name})

    return json_structure


def read_proto_files(service_file_path, message, message_resource_prefix_dict):
    with open(service_file_path, 'r') as service_file:
        extract_resource_name_mask(service_file.read(), message, message_resource_prefix_dict)


def extract_resource_name_mask(protobuf_message, message_name, message_resource_prefix_dict):
    # Define a regular expression pattern
    pattern = rf'{message_name}\.(.*?)\s*=\s*\d+\s*\[\s*\('+KEY_PROTO_ENTITY_NAME+'\.resource_name_mask\) = "(.*?)"\s*\];'
    # Use re.search to find the pattern in the protobuf_message
    match = re.search(pattern, protobuf_message, re.DOTALL)

    # Check if a match is found
    if match:
        resource_name_mask_value = match.group(2)
        resource_name_mask_value = resource_name_mask_value.rstrip('.*')

        if len(resource_name_mask_value) > 0:
            message_resource_prefix_dict.append({f"{message_name}": resource_name_mask_value})
    else:
        return "Resource Name Mask not found."


def get_protobuf_descriptor_data():
    node_json = []
    method_nodes = []
    for importer, modname, ispkg in pkgutil.walk_packages(path=proto.__path__, prefix=proto.__name__ + ".",
                                                          onerror=lambda x: print(f"Error parsing {x}")):
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
                    if field.name == 'id':
                        service_id = value
                    elif field.name == 'name':
                        service_name = value
                    else:
                        if field.name == 'version_major':
                            version = value
                        properties.append({"name": field.name, "value": value})
                service_json["node"] = create_service_json(service_name, version, service_id, properties)

                method_nodes = []
                for method in service_descriptor.methods_by_name.keys():
                    # get method object
                    options = service_descriptor.methods_by_name[method].GetOptions()
                    for field, value in options.ListFields():
                        if field.name == 'method_id':
                            method_id = value
                            method_nodes.append(create_method_json(f"{KEY_URI_PREFIX}:/{service_name}/{version}", method, method_id))
                message_option_descriptor = mod.DESCRIPTOR.message_types_by_name
                for message in message_option_descriptor.keys():
                    if 'Options' in message:
                        read_proto_files(
                            os.path.join(PROTO_REPO_DIR, 'src', 'main', 'proto', os.path.normpath(mod.DESCRIPTOR.name)),
                            message.replace('Options', ''), message_resource_prefix_dict)
                        if any(key in message_option_descriptor[message].fields_by_name.keys() for key in
                               ['resource_name', 'name']):
                            for field, value in message_option_descriptor[message].GetOptions().ListFields():
                                if field.name == 'base_topic_id':
                                    message_options_dict.append({f"{message.replace('Options', '')}": value})
                                    break

                service_json["node"]["node"] = method_nodes

            try:
                if service_json["node"] != {}:
                    messages = mod.DESCRIPTOR.message_types_by_name.keys()
                    topic_nodes = []
                    # Process messages
                    for message in messages:
                        message_mod = mod.DESCRIPTOR.message_types_by_name[message]

                        if (
                                'Resources' in message_mod.enum_types_by_name or 'Resource' in
                                message_mod.enum_types_by_name):
                            resources_key = 'Resources' if 'Resources' in message_mod.enum_types_by_name else 'Resource'
                            resources = message_mod.enum_types_by_name[resources_key].values_by_name.keys()
                            value = next((d[message] for d in message_options_dict if message in d), 0)
                            base_topic_id = value
                            for resource in resources:
                                topic_id = base_topic_id + message_mod.enum_types_by_name[resources_key].values_by_name[
                                    resource].number
                                topic_nodes.append(
                                    create_topic_json(f"{KEY_URI_PREFIX}:/{service_name}/{version}", resource, message_mod.name,
                                                      topic_id, message_mod.full_name, message_resource_prefix_dict))

                    if service_json and topic_nodes and len(topic_nodes) > 0:
                        service_json["node"]["node"] = service_json["node"]["node"] + topic_nodes
                        node_json.append(service_json)
                        service_json = None
            except Exception:
                continue

    resource_catalog_json = {"node": node_json}
    return resource_catalog_json


def write_topics_to_csv_file():
    csv_file_path = os.path.join(RESOURCE_CATALOG_DIR, RESOURCE_CATALOG_CSV_NAME)
    with open(csv_file_path, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        for topic_info in topic_list:
            csv_writer.writerow([topic_info['uri'], topic_info['package']])


def write_nodes_to_json_file(resource_catalog_json):
    # Write JSON data to the services.json
    if not os.path.exists(RESOURCE_CATALOG_DIR):
        os.makedirs(RESOURCE_CATALOG_DIR)
    json_file_path = os.path.join(RESOURCE_CATALOG_DIR, RESOURCE_CATALOG_JSON_NAME)
    with open(json_file_path, 'w') as json_file:
        json.dump(resource_catalog_json, json_file, indent=2)


def execute():
    write_nodes_to_json_file(get_protobuf_descriptor_data())
    write_topics_to_csv_file()


if __name__ == "__main__":
    execute()
