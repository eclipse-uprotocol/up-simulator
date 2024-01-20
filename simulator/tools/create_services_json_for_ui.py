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

import os
import re
import json

import simulator.utils.constant as CONSTANTS


def process_proto(directory):
    data = []
    for root, dirs, files in os.walk(directory):
        service_file_path = next((os.path.join(root, file) for file in files if file.endswith(CONSTANTS.SERVICE_PROTO_SUFFIX)),
                                 None)
        topic_file_path = next((os.path.join(root, file) for file in files if file.endswith(CONSTANTS.TOPIC_PROTO_SUFFIX)), None)
        if service_file_path and topic_file_path:
            service_content, topic_content = read_proto_files(service_file_path, topic_file_path)
            extract_proto_info(data, service_content, topic_content)

    return data


def read_proto_files(service_file_path, topic_file_path):
    with open(service_file_path, 'r') as service_file, open(topic_file_path, 'r') as topic_file:
        return service_file.read(), topic_file.read()


def extract_proto_info(data, service_file_content, topic_file_content):
    # Extract service name
    service_name = re.search(r'service\s+(\w+)\s*{', service_file_content)

    # Extract uprotocol name
    uprotocol_name = re.search(r'option\s+\(uprotocol\.name\)\s*=\s*"([^"]+)"', service_file_content)

    # Extract list of RPCs
    rpcs = re.findall(r'rpc\s+(\w+)\s*\(\s*[^)]*\s*\)', service_file_content) or []

    messages = re.findall(r'message\s+(\w+)\s*{', topic_file_content) or []

    append_to_data(data, uprotocol_name, service_name, rpcs, messages)


def append_to_data(data, uprotocol_name_match, service_name_match, rpcs, messages):
    json_obj = {"name": uprotocol_name_match.group(1) if uprotocol_name_match else None,
                "display_name": service_name_match.group(1) if service_name_match else None, "rpc": rpcs,
                "message": messages}
    data.append(json_obj)


if __name__ == "__main__":
    result_data = process_proto(CONSTANTS.PROTO_REPO_DIR)
    # Create the directory if it doesn't exist
    json_dir = os.path.join('..','..',CONSTANTS.UI_JSON_DIR)
    if not os.path.exists(json_dir):
        os.makedirs(json_dir)
    SERVICES_JSON_FILE_PATH = os.path.join(json_dir,CONSTANTS.SERVICES_JSON_FILE_NAME)
    # Write JSON data to the services.json
    with open(SERVICES_JSON_FILE_PATH, 'w') as json_file:
        json.dump(result_data, json_file, indent=2)
