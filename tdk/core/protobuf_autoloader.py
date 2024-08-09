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
import pathlib
import pkgutil
import random
import re
import traceback
from collections import defaultdict

from google.protobuf.descriptor import FieldDescriptor
from uprotocol.v1.uri_pb2 import UUri

from tdk.target import protofiles as proto
from tdk.utils.constant import (
    RESOURCE_CATALOG_CSV_NAME,
    RESOURCE_CATALOG_JSON_NAME,
)

rpc_methods = {}
rpc_fullname_methods = {}
rpc_topics = {}
topic_messages = []
message_to_module = {}
service_id = {}
entity_descriptor = {}
events_to_event_id_url = {}


# Protobuf autoloader functions. This module will automatically
# parse the python protobufs included in the protofiles folder
# and generate a map of rpc method names and their respective
# request protobuf message and response protobuf message.
# The protobuf classes can then be instantiated directly
# just by knowing the rpc method name and without having to import
# the protobuf definitions. See get_request_class()
# and get_response_class() below.


def populate_protobuf_classes():
    global rpc_methods
    global rpc_topics
    global topic_messages
    global rpc_fullname_methods
    global service_id

    cwd = pathlib.Path(__file__).parent.resolve()
    # Specify the relative path to the CSV file
    relative_path = os.path.abspath(os.path.join(cwd, "../target/resource_catalog"))
    # Combine the current working directory and the relative path
    csv_file_path = relative_path + os.sep + RESOURCE_CATALOG_CSV_NAME
    with open(csv_file_path, "r") as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            (uri, message_full_name) = row
            tmp = [uri.strip(), message_full_name.strip()]
            topic_messages.append(tmp)
    json_file_path = relative_path + os.sep + RESOURCE_CATALOG_JSON_NAME

    with open(json_file_path, "r") as json_file:
        json_data = json_file.read()
        resource_catalog = json.loads(json_data)
        try:
            parent_node = resource_catalog["node"]
            for service_node in parent_node:
                service_node = service_node["node"]
                uri = service_node["uri"]
                groups = re.search(r"/([\w\.]+)/([0-9\.]+)", uri)
                if groups:
                    service_name = groups.group(1)
                    service_id[service_name] = service_node["id"]

                topics_list = [item[0] for item in topic_messages]
                for endpoint in service_node["node"]:
                    events_to_event_id_url[endpoint["uri"]] = endpoint["uri_id"]
                    # Get the id of topic and store it- this id is needed for SOME IP integration
                    if endpoint["type"] == "topic":
                        uri = endpoint["uri"]
                        topics_list.index(uri)
                        topic_messages[topics_list.index(endpoint["uri"])].append(endpoint["uri_id"])

                    if endpoint["type"] == "method":
                        uri = endpoint["uri"]
                        groups = re.search(r"/([\w\.]+)/([0-9\.]+)/rpc.(\w+)", uri)
                        if groups:
                            service_name = groups.group(1)
                            api_version = int(
                                float(groups.group(2))
                            )  # this is really a semver but simulationproxy only uses ints.
                            name = groups.group(3)
                            if service_name not in rpc_topics.keys():
                                rpc_topics[service_name] = {}
                            if name not in rpc_topics[service_name].keys():
                                rpc_topics[service_name][name] = {
                                    "uri": [],
                                    "uri_id": [],
                                    "versions": [],
                                    "id": "",
                                }
                                rpc_topics[service_name][name]["versions"].append(api_version)
                                rpc_topics[service_name][name]["uri"].append(uri)
                                rpc_topics[service_name][name]["id"] = endpoint["id"]
                                rpc_topics[service_name][name]["uri_id"] = endpoint["uri_id"]
                            elif api_version not in rpc_topics[service_name][name]["versions"]:
                                rpc_topics[service_name][name]["versions"].append(api_version)
                                rpc_topics[service_name][name]["uri"].append(uri)
                                rpc_topics[service_name][name]["id"] = endpoint["id"]
                                rpc_topics[service_name][name]["uri_id"] = endpoint["uri_id"]

                            else:
                                print(f"Warning: possible duplicate method name detected for {uri}")
                        else:
                            print(f"Warning: RPC method name and service name could not be determined for {uri}")
        except Exception:
            print("Warning: except occurred during parsing of Resource Catalog:")
            traceback.print_exc()

        get_protobuf_descriptor_data()

        return rpc_methods


# ex- given_uri="/999/1/32768"
def get_uuri_from_id(given_uri: str) -> UUri:
    split_parts = given_uri.split('/')
    return UUri(
        authority_name=split_parts[0],
        ue_id=int(split_parts[1]),
        ue_version_major=int(split_parts[2]),
        resource_id=int(split_parts[3]),
    )


# ex- given_uri="/example.hello_world/1/one_second#Timer"
def get_uuri_from_name(given_uri: str) -> UUri:
    if given_uri in events_to_event_id_url:
        return get_uuri_from_id(events_to_event_id_url[given_uri])
    return UUri()


def get_uri_str_from_uuri(given_uri: UUri) -> str:
    for key, value in events_to_event_id_url.items():
        if value == given_uri:
            return key


def get_entity_name_from_entity_id(id):
    for key in service_id:
        if service_id[key] == id:
            return key


def get_entity_id_from_entity_name(service_name):
    return service_id[service_name]


def get_method_uri_id_from_method_name(entity, rpc_method_name) -> str:
    return rpc_topics[entity][rpc_method_name]["uri_id"]


def get_method_name_from_method_id(entity_id, rpc_method_id):
    if not isinstance(entity_id, str):
        entity_id = str(entity_id)
    if not isinstance(rpc_method_id, str):
        rpc_method_id = str(rpc_method_id)
    for method_name, method_dict in rpc_methods[entity_id].items():
        if method_dict["id"] == rpc_method_id:
            return method_name


def get_protobuf_descriptor_data():
    global entity_descriptor
    for importer, modname, ispkg in pkgutil.walk_packages(
        path=proto.__path__,
        prefix=proto.__name__ + ".",
        onerror=lambda x: print(f"Error parsing {x}"),
    ):
        mod = importlib.import_module(modname)
        try:
            _services = mod.DESCRIPTOR.services_by_name.keys()
        except Exception:
            continue
        services = []
        for service in _services:
            for field, value in mod.DESCRIPTOR.services_by_name[service].GetOptions().ListFields():
                if field.name in ["service_name", "name"]:
                    protobuf_service = value
                if field.name in ["service_id", "id"]:
                    protobuf_id = str(value)

            entity_descriptor[protobuf_service] = mod.DESCRIPTOR.services_by_name[service]
            services.append((service, protobuf_service))
        messages = mod.DESCRIPTOR.message_types_by_name.keys()
        for message in messages:
            if message in message_to_module:
                print(f"WARNING: Duplicate message type detected for {message}")
                print(f"{mod.DESCRIPTOR.message_types_by_name[message].full_name}")
                print(f"{message_to_module[message]}")
            message_to_module[mod.DESCRIPTOR.message_types_by_name[message].full_name] = modname

        for service, protobuf_service in services:
            for method in mod.DESCRIPTOR.services_by_name[service].methods_by_name.keys():
                # get method object
                m = mod.DESCRIPTOR.services_by_name[service].methods_by_name[method]

                rpc_info = parse_method(protobuf_service, rpc_method=m, containing_module=modname)
                if rpc_info is None:
                    continue

                if protobuf_id not in rpc_methods.keys():
                    rpc_methods[protobuf_id] = {}
                rpc_methods[protobuf_id][m.name] = rpc_info

                rpc_fullname_methods[m.full_name] = rpc_info


def get_request_class(service_id, rpc_name):
    if not isinstance(service_id, str):
        service_id = str(service_id)
    global rpc_methods
    return rpc_methods[service_id][rpc_name]["request"]


def get_topics_by_proto_service_id(service_id):
    global topic_messages
    topics = []
    for pair in topic_messages:
        if len(pair) < 3:
            continue
        topic = pair[2]
        if "/" + service_id + "/" in topic:
            topics.append(pair[0])

    return topics


def get_services():
    global service_id
    return service_id.values()


# returns a class object for the response message for a given rpc method name
def get_response_class(service_id, rpc_name):
    if not isinstance(service_id, str):
        service_id = str(service_id)
    global rpc_methods
    return rpc_methods[service_id][rpc_name]["response"]


def parse_method(service_name, rpc_method, containing_module):
    input_class = find_message_class(containing_module, rpc_method.input_type.full_name)
    output_class = find_message_class(containing_module, rpc_method.output_type.full_name)
    try:
        (versions, uri, uri_id) = get_rpc_method_uri(service_name, rpc_method)
    except Exception:
        print(f"ERROR: URI not found for RPC method {rpc_method.name} in service {service_name}.")
        return None
    if uri is not None:
        uri = uri

    return {
        "request": input_class,
        "response": output_class,
        "full_name": rpc_method.full_name,
        "module": containing_module,
        "service": service_name,
        "uri": uri,
        "versions": versions,
        "id": uri_id,
    }


def find_message_class(containing_module, class_full_name):
    class_base_name = class_full_name.rsplit(".", maxsplit=1)[1]

    try:
        # look in services protobuf file
        class_obj = getattr(importlib.import_module(containing_module), class_base_name)
    except (ModuleNotFoundError, AttributeError):
        try:
            # look in topics protobuf file
            class_obj = getattr(
                importlib.import_module(containing_module.replace("service", "topics")),
                class_base_name,
            )
        except (ModuleNotFoundError, AttributeError):
            try:
                # try absolute import
                class_obj = getattr(
                    importlib.import_module(
                        class_full_name.rsplit(".", maxsplit=1)[0] + "." + class_base_name.lower() + "_pb2"
                    ),
                    class_base_name,
                )
            except (ModuleNotFoundError, AttributeError):
                try:
                    # try wellknown types
                    class_obj = getattr(
                        importlib.import_module("google.protobuf.wrappers_pb2"),
                        class_base_name,
                    )
                except (ModuleNotFoundError, AttributeError):
                    print(f"WARNING: Unable to find protobuf definition for {class_full_name}")
                    class_obj = None

    return class_obj


# returns the uri for a given rpc method name
# param method is the protobuf object
# see get_rpc_uri_by_name for looking up
# the uri based on just the method name
def get_rpc_method_uri(service, method):
    global rpc_topics
    for field, value in method.GetOptions().ListFields():
        if field.name == "method_id":
            method_id = str(value)

    method_name = method.name
    if service in rpc_topics.keys():
        for method in rpc_topics[service].keys():
            if method_name == method:
                return rpc_topics[service][method]["versions"], str(rpc_topics[service][method]["uri"]), method_id

    return None


# given a message class, return a list of it's field names
def get_message_fields(message_class):
    return message_class.DESCRIPTOR.fields_by_name.keys()


# recursively populate protobufs using a nested dictionary
def _populate_message(service_name, message_class, data_dict):
    service_id = get_entity_id_from_entity_name(service_name)
    fields = get_message_fields(message_class)

    _next_args = {}

    # gather the names of any OneOfs
    oneofs = []

    # to gather all the oneof fields
    for field in message_class.DESCRIPTOR.oneofs:
        # there is a bug in the protobuf library where optional fields also appear in message.DESCRIPTOR.oneofs.
        # we can differentiate between optional and oneof fields by checking the number of fields.
        # optional fields will only have 1 field, whereas oneof fields will have more than one.
        if len(field.fields) > 1:
            oneofs.append(field.name)
    oneofs = set(oneofs)
    input_fields = set(data_dict.keys())
    inputs_fields_that_are_oneofs = input_fields.intersection(oneofs)

    if len(inputs_fields_that_are_oneofs) > 1:
        raise Exception(f"Your input dictionary has multiple fields of a composite OneOf field.\
 Only one of the OneOf fields may be accepted.\nMessage class: {message_class}\nOneOf fields: {oneofs}")

    for field in fields:
        # Handled unsupported enum exception, if the enum is unsupported, generate random number which is not present
        # in the enum list
        try:
            if message_class.DESCRIPTOR.fields_by_name[field].enum_type is not None:
                if (
                    field in data_dict
                    and (not isinstance(data_dict[field], int))
                    and data_dict[field] not in message_class.DESCRIPTOR.fields_by_name[field].enum_type.values_by_name
                ):
                    # enum value not present, handle exception
                    # Generate random numbers until one is not in the list
                    while True:
                        rand_num = random.randint(1, 100)
                        if rand_num not in message_class.DESCRIPTOR.fields_by_name[field].enum_type.values_by_number:
                            break
                    data_dict[field] = rand_num
        except Exception:
            pass
        # end

        arg = message_class.DESCRIPTOR.fields_by_name[field]
        # if the field is a pointer to another message, go get that message
        if arg.type == FieldDescriptor.TYPE_MESSAGE:
            _next = find_message(arg.message_type.full_name)
            # make sure data_dict is a dict
            if isinstance(data_dict, dict):
                # handle lists of repeated messages
                if field in data_dict and isinstance(data_dict[field], list):
                    new_messages = []

                    # get the message type for the field
                    list_type = str(arg.message_type.name)

                    # get the class for the repeated message type
                    list_class = find_request_by_type(service_id, list_type)

                    for subfields in data_dict[field]:
                        nested_message = _populate_message(service_name, list_class, subfields)
                        new_messages.append(nested_message)

                    _next_args[field] = new_messages

                # check if dict is nested
                elif field in data_dict and bool(data_dict[field]):
                    nested_message = _populate_message(service_name, _next, data_dict[field])
                    _next_args[field] = nested_message

        else:
            # skip populating if field is empty
            if field in data_dict and data_dict[field]:
                _next_args[field] = data_dict[field]

    # make sure a list is defined for repeated values
    for field in get_message_fields(message_class):
        if isinstance(message_class.DESCRIPTOR.fields_by_name[field].default_value, list):
            if field in _next_args:
                tmp = _next_args[field]
                if not isinstance(tmp, list):
                    _next_args[field] = []
                    _next_args[field].append(tmp)

    return message_class(**_next_args)


# returns the message class for a given message name
def find_message(message_full_name):
    message_class = None
    module = None
    try:
        module = message_to_module[message_full_name]
        message_class = find_message_class(module, message_full_name)
    except Exception:
        (containing_message, basename) = message_full_name.rsplit(".", 1)
        try:
            module = message_to_module[containing_message]
            message_class = find_message_class(module, containing_message)
        except Exception:
            if containing_message.startswith("google.type"):
                from google import type as google_type

                for loader, modname, ispkg in pkgutil.walk_packages(google_type.__path__):
                    mod = importlib.import_module("google.type." + modname)
                    try:
                        message_class = getattr(mod, basename)
                        return message_class
                    except Exception:
                        continue
            elif containing_message.startswith("google"):
                from google import protobuf as google_protobuf

                for loader, modname, ispkg in pkgutil.walk_packages(google_protobuf.__path__):
                    mod = importlib.import_module("google.protobuf." + modname)
                    try:
                        message_class = getattr(mod, basename)
                        return message_class
                    except Exception:
                        continue
        if message_class is None:
            print(f'Message class not available in proto for {message_full_name}')
            return None
        return getattr(message_class, basename)

    return message_class


# returns a class object for the request message for a given topic uri
def get_request_class_from_topic_uri(given_topic):
    for topic in topic_messages:
        if given_topic in topic:
            modname = message_to_module[topic[1]]
            message_class = find_message_class(modname, topic[1])
            return message_class


# public wrapper around unpack_data_dict and _populate_message
def populate_message(service_name, message_class, data_dict):
    data_dict = unpack_data_dict(data_dict)
    return _populate_message(service_name, message_class, data_dict)


def default_factory():
    return defaultdict(default_factory)


# normalize a dictionary with nested protobufs defined as dict keys with dot-notation
# into a nested dictionary
def unpack_data_dict(data_dict):
    _defaultdict = default_factory
    new_dict = _defaultdict()
    if not isinstance(data_dict, dict):
        return data_dict
    for key in data_dict.keys():
        value = data_dict[key]
        # recurse through nested structures
        if isinstance(value, dict):
            value = unpack_data_dict(value)
        if isinstance(value, list):
            new_value = []
            for i in value:
                new_value.append(unpack_data_dict(i))
            value = new_value

        # split keys into nested structures
        exploded_key = key.split(".")
        # there has to be a better way but i have a deadline.
        # open to suggestions during code review.
        # currently support up to 10 nested structures.
        # i'm sure there's a way to deference a nested dict of
        # an arbitrary number of levels...but i have no idea how and
        # google is not helping.
        if len(exploded_key) == 10:
            new_dict[exploded_key[0]][exploded_key[1]][exploded_key[2]][exploded_key[3]][exploded_key[4]][
                exploded_key[5]
            ][exploded_key[6]][exploded_key[7]][exploded_key[8]][exploded_key[9]] = value
        if len(exploded_key) == 9:
            new_dict[exploded_key[0]][exploded_key[1]][exploded_key[2]][exploded_key[3]][exploded_key[4]][
                exploded_key[5]
            ][exploded_key[6]][exploded_key[7]][exploded_key[8]] = value
        if len(exploded_key) == 8:
            new_dict[exploded_key[0]][exploded_key[1]][exploded_key[2]][exploded_key[3]][exploded_key[4]][
                exploded_key[5]
            ][exploded_key[6]][exploded_key[7]] = value
        if len(exploded_key) == 7:
            new_dict[exploded_key[0]][exploded_key[1]][exploded_key[2]][exploded_key[3]][exploded_key[4]][
                exploded_key[5]
            ][exploded_key[6]] = value
        if len(exploded_key) == 6:
            new_dict[exploded_key[0]][exploded_key[1]][exploded_key[2]][exploded_key[3]][exploded_key[4]][
                exploded_key[5]
            ] = value
        if len(exploded_key) == 5:
            new_dict[exploded_key[0]][exploded_key[1]][exploded_key[2]][exploded_key[3]][exploded_key[4]] = value
        if len(exploded_key) == 4:
            new_dict[exploded_key[0]][exploded_key[1]][exploded_key[2]][exploded_key[3]] = value
        if len(exploded_key) == 3:
            new_dict[exploded_key[0]][exploded_key[1]][exploded_key[2]] = value
        elif len(exploded_key) == 2:
            new_dict[exploded_key[0]][exploded_key[1]] = value
        elif len(exploded_key) == 1:
            new_dict[key] = value
    return new_dict


def find_request_by_type(service_id, message_type):
    global rpc_methods
    for method in rpc_methods[service_id].keys():
        if message_type == rpc_methods[service_id][method]["request"].DESCRIPTOR.full_name.split(".")[-1]:
            return rpc_methods[service_id][method]["request"]

    service = get_entity_name_from_entity_id(service_id)
    for message, module in message_to_module.items():
        if service in message and message_type == message.split(".")[-1]:
            return find_message(message)


def get_rpc_uri_by_name(service_id, rpc_method_name, uri_version=None):
    service_name = get_entity_name_from_entity_id(service_id)
    global rpc_topics
    # dont try/except since not finding the URI is a major issue
    if uri_version is not None:
        for uri in rpc_topics[service_name][rpc_method_name]["uri"]:
            if int(re.search(r"/([\w\.]+)/([0-9\.]+)/rpc.(\w+)", uri).group(2)) == uri_version:
                return uri
    else:
        uri_version = 0
    return str(rpc_topics[service_name][rpc_method_name]["uri"][uri_version])


# returns a dict of all {rpc_method: request_class_path}
def get_request_map(service_id):
    global rpc_methods
    request_map = {}
    for i in rpc_methods[service_id].keys():
        # if rpc_methods[service_id][i]["service"] == service or service is None:
        request_map[i] = (
            str(rpc_methods[service_id][i]["request"].__module__)
            + "."
            + str(rpc_methods[service_id][i]["request"].__qualname__)
        )

    return request_map


# returns a dict of all {rpc_method: request_class_path}
def get_response_map(service_id=None):
    global rpc_methods
    response_map = {}
    for i in rpc_methods[service_id].keys():
        # if rpc_methods[service_id][i]["service"] == service or service is None:
        response_map[i] = (
            str(rpc_methods[service_id][i]["response"].__module__)
            + "."
            + str(rpc_methods[service_id][i]["response"].__qualname__)
        )

    return response_map


def get_topic_map():
    global topic_messages
    topic_map = {}
    for topic in topic_messages:
        if len(topic) == 2:
            continue
        if len(topic) == 3:
            url, msg_type, uri_id = topic
        else:
            print(topic)
            url, msg_type, uri_id, extra_param = topic
        msg_base_name = msg_type.rsplit(".")[-1]
        try:
            containing_module = message_to_module[msg_type]
        except KeyError:
            continue
        topic_map[uri_id] = f"{containing_module}.{msg_base_name}"
    return topic_map


# returns a list of tuples of (uri, message class) for a given service name
def get_topics_by_service(service_name):
    global topic_messages
    ret = []
    if service_name is None:
        return ret
    for topic in topic_messages:
        if ("/" + service_name + "/") in topic[0]:
            modname = message_to_module[topic[1]]
            message_class = find_message_class(modname, topic[1])
            ret.append((topic[0], message_class))
    return ret


# returns a list of rpc method names based on service name
def get_methods_by_service(service_id):
    global rpc_methods
    ret = {}
    if service_id in rpc_methods:
        for method in rpc_methods[service_id].keys():
            ret[method] = rpc_methods[service_id][method]
    return ret


# populate on import
populate_protobuf_classes()

uri_id_to_message_module_map = get_topic_map()
