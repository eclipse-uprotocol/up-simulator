# -------------------------------------------------------------------------
#
# Copyright (c) 2023 General Motors GTO LLC
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
# SPDX-FileCopyrightText: 2023 General Motors GTO LLC
# SPDX-License-Identifier: Apache-2.0
#
# -------------------------------------------------------------------------

import csv
import importlib
import json
import os
import pathlib
import pkgutil
import re
import traceback

import protofiles as proto

rpc_methods = {}
rpc_fullname_methods = {}
rpc_topics = {}
topic_messages = []
message_to_module = {}
service_id = {}


# Protobuf autoloader functions. This module will automatically
# parse the python protobufs included in the sdv_simulation library
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
    # see comment below.
    rpc_methods[None] = {}

    cwd = pathlib.Path(__file__).parent.resolve()
    # Specify the relative path to the CSV file
    relative_path = os.path.abspath(os.path.join(cwd, ".." + os.sep + "core"))
    # Combine the current working directory and the relative path
    csv_file_path = relative_path + os.sep + "ResourceCatalog.csv"
    with open(csv_file_path, 'r') as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            (uri, message_full_name) = row
            tmp = [uri.strip(), message_full_name.strip()]
            topic_messages.append(tmp)
    json_file_path = relative_path + os.sep + "ResourceCatalog.json"

    with open(json_file_path, 'r') as json_file:
        json_data = json_file.read()
        resource_catalog = json.loads(json_data)
        try:
            parent_node = resource_catalog["node"]
            for service_node in parent_node:
                service_node = service_node["node"]
                uri = service_node['uri']
                groups = re.search(r"/([\w\.]+)/([0-9\.]+)", uri)
                if groups:
                    service_name = groups.group(1)
                    service_id[service_name] = service_node["id"]

                topics_list = [item[0] for item in topic_messages]
                for endpoint in service_node["node"]:
                    # Get the id of topic and store it- this id is needed for SOME IP integration
                    if endpoint['type'] == 'topic':
                        uri = endpoint['uri']
                        topics_list.index(uri)
                        topic_messages[topics_list.index(endpoint['uri'])].append(endpoint["id"])

                    if endpoint['type'] == 'method':
                        uri = endpoint['uri']
                        groups = re.search(r"/([\w\.]+)/([0-9\.]+)/rpc.(\w+)", uri)
                        if groups:
                            service_name = groups.group(1)
                            api_version = int(
                                float(groups.group(2)))  # this is really a semver but simulationproxy only uses ints.
                            name = groups.group(3)
                            if service_name not in rpc_topics.keys():
                                rpc_topics[service_name] = {}
                            if name not in rpc_topics[service_name].keys():
                                rpc_topics[service_name][name] = {"uri": [], "versions": [], "id": ""}
                                rpc_topics[service_name][name]["versions"].append(api_version)
                                rpc_topics[service_name][name]["uri"].append(uri)
                                rpc_topics[service_name][name]["id"] = endpoint["id"]
                            elif api_version not in rpc_topics[service_name][name]["versions"]:
                                rpc_topics[service_name][name]["versions"].append(api_version)
                                rpc_topics[service_name][name]["uri"].append(uri)
                                rpc_topics[service_name][name]["id"] = endpoint["id"]

                            else:
                                print(f"Warning: possible duplicate method name detected for {uri}")
                        else:
                            print(f"Warning: RPC method name and service name could not be determined for {uri}")
        except:
            print("Warning: except occured during parsing of Resource Catalog:")
            traceback.print_exc()

        for importer, modname, ispkg in pkgutil.walk_packages(path=proto.__path__, prefix=proto.__name__ + ".",
                                                              onerror=lambda x: print(f"Error parsing {x}")):

            services = []

            mod = importlib.import_module(modname)
            try:
                _services = mod.DESCRIPTOR.services_by_name.keys()
            except:
                continue
            services = []
            for service in _services:
                options = str(mod.DESCRIPTOR.services_by_name[service].GetOptions())
                groups = re.search(r"^\[ultifi\.name\]:\s\"([\w.]+)\"$", options, re.MULTILINE)
                try:
                    protobuf_service = groups.group(1)
                except:
                    print(options)
                    continue
                services.append((service, protobuf_service))
            messages = mod.DESCRIPTOR.message_types_by_name.keys()
            for message in messages:
                if message in message_to_module:
                    print(f"WARNING: Duplicate message type detected for {message}")
                    print(f"{mod.DESCRIPTOR.message_types_by_name[message].full_name}")
                    print(f"{message_to_module[message]}")
                message_to_module[mod.DESCRIPTOR.message_types_by_name[message].full_name] = modname

            for (service, protobuf_service) in services:
                for method in mod.DESCRIPTOR.services_by_name[service].methods_by_name.keys():

                    # get method object
                    m = mod.DESCRIPTOR.services_by_name[service].methods_by_name[method]
                    rpc_info = parse_method(protobuf_service, rpc_method=m, containing_module=modname)
                    if rpc_info is None:
                        continue
                    if rpc_info['full_name'] in rpc_methods.keys():
                        if rpc_info['full_name'] != rpc_methods[rpc_info['name']]['full_name']:
                            print('*' * 60)
                            print(f"WARNING: Duplicate RPC method name detected: {m.name}:")
                            print("If you see this message, please email philip.1.behnke@gm.com")
                            print(f"{rpc_info['full_name']}")
                            print(f"{rpc_methods[rpc_info['name']]['full_name']}")
                            print('*' * 60)
                    if protobuf_service not in rpc_methods.keys():
                        rpc_methods[protobuf_service] = {}
                    rpc_methods[protobuf_service][m.name] = rpc_info
                    # for legacy purposes, keep a dict keyed only by method name when service is None.
                    # for methods of the same name but in different services, we can only keep the last method
                    # processed.
                    # this is to ease migration to passing in the service name, which we haven't done historically
                    rpc_methods[None][m.name] = rpc_info
                    rpc_fullname_methods[m.full_name] = rpc_info

        return rpc_methods


def parse_method(service, rpc_method, containing_module):
    input_class = find_message_class(containing_module, rpc_method.input_type.full_name)
    output_class = find_message_class(containing_module, rpc_method.output_type.full_name)
    try:
        (versions, uri) = get_rpc_method_uri(service, rpc_method)
    except:
        print(f"ERROR: URI not found for RPC method {rpc_method.name} in service {service}.")
        return None
    if uri != None:
        uri = uri

    return {"request": input_class, "response": output_class, "full_name": rpc_method.full_name,
            "module": containing_module, "service": service, "uri": uri, "versions": versions}


def find_message_class(containing_module, class_full_name):
    class_base_name = class_full_name.rsplit(".", maxsplit=1)[1]

    try:
        # look in services protobuf file
        class_obj = getattr(importlib.import_module(containing_module), class_base_name)
    except (ModuleNotFoundError, AttributeError):
        try:
            # look in topics protobuf file
            class_obj = getattr(importlib.import_module(containing_module.replace("service", "topics")),
                                class_base_name, )
        except (ModuleNotFoundError, AttributeError):
            try:
                # try absolute import
                class_obj = getattr(importlib.import_module(
                    class_full_name.rsplit(".", maxsplit=1)[0] + "." + class_base_name.lower() + "_pb2"),
                    class_base_name, )
            except (ModuleNotFoundError, AttributeError):
                try:
                    # try wellknown types
                    class_obj = getattr(importlib.import_module("google.protobuf.wrappers_pb2"), class_base_name, )
                except (ModuleNotFoundError, AttributeError):
                    # check for messages contained in protobuf definitions not using standard naming convention
                    if class_base_name == "SetLampRequest" or class_base_name == "SetLampsRequest":
                        class_obj = getattr(
                            importlib.import_module("protofiles.ultifi.vehicle.body.lighting.v1.set_lamps_request_pb2"),
                            class_base_name, )
                    elif class_base_name == "UriRequest" or class_base_name == "UriResponse":
                        class_obj = getattr(importlib.import_module("protofiles.ultifi.core.uri_pb2"),
                                            class_base_name, )
                    elif class_base_name == "Topic":
                        class_obj = getattr(importlib.import_module("protofiles.ultifi.core.topic_pb2"),
                                            class_base_name, )
                    elif class_base_name == "CloudEvent":
                        class_obj = getattr(importlib.import_module("protofiles.io.cloudevents.v1.cloudevents_pb2"),
                            class_base_name, )
                    else:
                        print(f"WARNING: Unable to find protobuf definition for {class_full_name}")
                        class_obj = None
    return class_obj


# returns the uri for a given rpc method name
# param method is the protobuf object
# see get_rpc_uri_by_name for looking up
# the uri based on just the method name
def get_rpc_method_uri(service, method):
    global rpc_topics
    method_name = method.name
    if service in rpc_topics.keys():
        for method in rpc_topics[service].keys():
            if method_name == method:
                return rpc_topics[service][method]["versions"], str(rpc_topics[service][method]["uri"])
    if service == "example.hello_world":
        return [1], "ultifi:/example.hello_world/1/rpc." + method.name
    return None


# populate on import
populate_protobuf_classes()
