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

from simulator.utils import constant
from tdk.core import protobuf_autoloader as autoloader

result_data = []


def get_messages(service_id):
    output = []
    for item in autoloader.get_topics_by_proto_service_id(service_id):
        status = item.split('#')[-1]
        output.append(status)
    unique_element = []
    seen = set()
    for item in output:
        if item not in seen:
            unique_element.append(item)
            seen.add(item)
    return unique_element


def get_display_name(input_str):
    parts = input_str.split('.')
    try:
        formatted_str = ' '.join(part.capitalize() for part in parts[1].split('_') + parts[2:] if part)
    except Exception:
        formatted_str = input_str.capitalize()
    return formatted_str


def execute():
    for service in autoloader.get_services():
        service_name = autoloader.get_entity_name_from_entity_id(service)
        if service_name not in ["core.utelemetry", "core.usubscription", "core.udiscovery"]:
            data_dict = {
                "name": service_name,
                "display_name": get_display_name(service_name),
                "rpc": list(autoloader.get_methods_by_service(service).keys()),
                "message": get_messages(service),
            }
            result_data.append(data_dict)

    # Create the directory if it doesn't exist
    if not os.path.exists(constant.UI_JSON_DIR):
        os.makedirs(constant.UI_JSON_DIR)
    services_json_file_path = os.path.join(constant.UI_JSON_DIR, constant.SERVICES_JSON_FILE_NAME)
    # Write JSON data to the services.json
    with open(services_json_file_path, 'w') as json_file:
        json.dump(result_data, json_file, indent=2)
        print("Service.json is created successfully")


if __name__ == "__main__":
    execute()
