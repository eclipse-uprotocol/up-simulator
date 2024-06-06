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

import logging
from importlib import import_module

from simulator.core.transport_layer import TransportLayer
from simulator.ui.utils import adb_utils

logger = logging.getLogger("CommonUtil")
reg_id = []


def verify_all_checks():
    is_by_pass = False
    env = TransportLayer().get_transport()

    if env != "BINDER":
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


def print_subscribe_status(topic, status_code, status_message):
    logger.debug("subscribe_status: Topic contents...")
    logger.debug(f"Topic: {topic}, Status Code: {status_code}, Status Message: {status_message}")
    if status_code == 0:
        logger.debug(f"Successfully subscribed for {topic}")
    else:
        logger.error(
            f"Unsuccessful subscription for {topic} as the status code is {status_code} with status message "
            f"{status_message}"
        )


def print_publish_status(topic, status_code, status_message):
    logger.debug("publish_status: Topic contents...")
    logger.debug(f"Topic: {topic}, Status Code: {status_code}, Status Message: {status_message}")
    if status_code == 0:
        logger.debug(f"Successfully published for {topic}")
    else:
        logger.error(
            f"Unsuccessful publish for {topic} as the status code is {status_code} with status message "
            f"{status_message}"
        )


def print_register_rpc_status(methoduri, status_code, status_message):
    logger.debug("register_rpc_status: contents...")
    logger.debug(f"Method uri: {methoduri}, Status Code: {status_code}, Status Message: {status_message}")
    if status_code == 0:
        logger.debug(f"Successfully subscribed for {methoduri}")
    else:
        logger.error(
            f"Unsuccessful subscription for {methoduri} as the status code is {status_code} with status message "
            f"{status_message}"
        )


def print_create_topic_status_handler(topic, status_code, status_message):
    logger.debug("create_topic_status: Topic contents...")
    logger.debug(f"Topic: {topic}, Status Code: {status_code}, Status Message: {status_message}")
    if status_code == 0:
        logger.debug(f"Successfully Created topic for {topic}")
    else:
        logger.error(
            f"Unsuccessful Creation of topic for {topic} as the status code is {status_code} "
            + f"with status message {status_message}"
        )
