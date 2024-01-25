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
import re
import subprocess
import time

from ppadb.client import Client as AdbClient
from pyaxmlparser import APK as APKParse
from packaging import version

logger = logging.getLogger("adb_utils")
apk_path = os.path.join(os.getcwd(), 'simulator', 'core', "uPAndroidProxy-debug.apk")
package_name = "org.eclipse.uprotocol.service.androidproxy"


def get_emulator_device():
    client = AdbClient(host="127.0.0.1", port=5037)  # Default is "127.0.0.1" and 5037
    devices = client.devices()
    if len(devices) == 0:
        print('No devices')
        return None
    else:
        return devices[0]


def get_installed_apk_version(package_name):
    try:
        result = subprocess.run(["adb", "shell", "dumpsys", "package", package_name], capture_output=True, text=True,
                                check=True)
        version_match = re.search(r"versionName=(\S+)", result.stdout)
        if version_match:
            return version_match.group(1)
        else:
            return None
    except subprocess.CalledProcessError:
        return None


def is_apk_installed(package_name):
    return get_installed_apk_version(package_name) is not None


def get_apk_version(apk_path):
    try:
        apk = APKParse(apk_path)
        local_version = version.parse(apk.version_name)
        return local_version
    except Exception as e:
        print("Error:", e)
        return None


def install_apk():
    if is_apk_installed(package_name):
        installed_version = get_installed_apk_version(package_name)
        apk_version = get_apk_version(apk_path).base_version

        if apk_version and installed_version != apk_version:
            print("Different version of APK is already installed. Installing the new version.")
            install_start_apk()
        else:
            start_apk()
    else:
        print("APK is not installed. Installing now.")
        install_start_apk()


def install_start_apk():
    try:
        forward_adb_port(6095)
        subprocess.run(["adb", "install", "-r", apk_path], check=True)
        print("APK installed successfully!")
        start_apk()
    except subprocess.CalledProcessError as e:
        print("Error:", e)


def is_app_running():
    try:
        output = subprocess.check_output(["adb", "shell", "pidof", package_name])
        return len(output.strip()) > 0
    except subprocess.CalledProcessError:
        return False


def start_apk():
    if not is_app_running():
        try:
            subprocess.run(["adb", "shell", "am", "start", "-n", f"{package_name}/.MainActivity"], check=True)
            print("APK started successfully!")
            time.sleep(5)
        except subprocess.CalledProcessError as e:
            print("Error:", e)


def is_adb_port_forwarded(port):
    try:
        result = subprocess.run(["adb", "forward", "--list"], capture_output=True, text=True, check=True)
        return f"tcp:{port}" in result.stdout and f"tcp:{port}" in result.stdout
    except subprocess.CalledProcessError:
        return False


def forward_adb_port(port):
    if not is_adb_port_forwarded(port):
        try:
            subprocess.run(["adb", "forward", f"tcp:{port}", f"tcp:{port}"], check=True)
            print(f"ADB port forwarding from {port} to {port} successful.")
        except subprocess.CalledProcessError as e:
            print("Error:", e)
    else:
        print(f"ADB port forwarding from {port} to {port} already exists.")
