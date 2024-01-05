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
import os
import telnetlib
import subprocess
from ppadb.client import Client as AdbClient

logger = logging.getLogger("adb_commands")


def adbcommands(cmd):
    sp = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    rc = sp.wait()
    print(f'{cmd} , {rc}')


def get_emulator_device():
    client = AdbClient(host="127.0.0.1", port=5037)  # Default is "127.0.0.1" and 5037
    devices = client.devices()
    if len(devices) == 0:
        print('No devices')
        return None
    else:
        print(len(devices))
        return devices[0]


def check_service_running_status(service):
    """Check if <service> is running."""
    try:
        findService = get_emulator_device().shell("ps -e -o NAME | grep " + service)
        assert service in findService
        logger.info("Process : " + findService + " running")

        running = True
    except AssertionError as e:
        logger.error(f'Assertion error:', exc_info=e)
        logger.debug(service + " not found")
        running = False

    return running
