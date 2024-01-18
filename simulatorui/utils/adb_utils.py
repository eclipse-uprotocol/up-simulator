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


import logging

from ppadb.client import Client as AdbClient

logger = logging.getLogger("adb_utils")


def get_emulator_device():
    client = AdbClient(host="127.0.0.1", port=5037)  # Default is "127.0.0.1" and 5037
    devices = client.devices()
    if len(devices) == 0:
        print('No devices')
        return None
    else:
        print(len(devices))
        return devices[0]
