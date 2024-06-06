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

import time

from simulator.tools import pull_and_compile_protos


def execute_pre_scripts():
    pull_and_compile_protos.execute()
    time.sleep(1)
    from simulator.tools import generate_resource_catalog

    generate_resource_catalog.execute()
    time.sleep(1)
    from simulator.tools import create_services_json_for_ui

    create_services_json_for_ui.execute()
    time.sleep(1)
    from simulator.tools import create_pub_sub_json_for_ui

    create_pub_sub_json_for_ui.execute()
    time.sleep(1)
    from simulator.tools import create_rpc_json_for_ui

    create_rpc_json_for_ui.execute()
    time.sleep(1)


if __name__ == "__main__":
    execute_pre_scripts()
