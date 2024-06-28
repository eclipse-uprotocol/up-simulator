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

from importlib import import_module

from simulator.ui.utils import adb_utils
from tdk.transport.transport_configuration import TransportConfiguration

reg_id = []


def verify_all_checks():
    is_by_pass = False
    env = TransportConfiguration().get_transport()

    if env != "SOCKET":
        is_by_pass = True

    if is_by_pass:
        return ""
    else:
        # check emulator is running or not
        device = adb_utils.get_emulator_device()
        message = ""
        if device is not None:
            try:
                status = device.shell("getprop init.svc.bootanim")
                if not status.__contains__("stopped"):
                    message = "Emulator is loading.."

            except Exception:
                message = "Emulator is loading.."

        else:
            message = "Emulator is not running.."

        return message


def flatten_dict(in_dict, prefix=""):
    new_dict = {}
    for k in in_dict.keys():
        v = in_dict[k]
        if isinstance(v, dict):
            new_prefix = prefix + "." + k if prefix else k
            new_dict.update(flatten_dict(v, prefix=new_prefix))

        else:
            new_k_name = prefix + "." + k if prefix else k
            new_dict[new_k_name] = v
    return new_dict


def get_class(full_name):
    """
    This function takes module and class name to import module and gets the object to the class
    """
    try:
        module_path, class_name = full_name.rsplit(".", 1)
        try:
            module = import_module(module_path)
        except ImportError:
            module = import_module("core.protofiles." + module_path)
        return getattr(module, class_name)
    except (ImportError, AttributeError):
        raise ImportError(full_name)
