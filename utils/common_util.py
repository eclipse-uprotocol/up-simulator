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
from importlib import import_module

from core import transport_layer

logger = logging.getLogger("CommonUtil")
reg_id = []


def verify_all_checks():
    global is_by_pass
    env = transport_layer.utransport

    if env != "Binder":
        is_by_pass = True

    if is_by_pass:
        return ''
    else:
        # todo for aidl binder- make sure that the tck proxy apk is installed
        pass

        return None


def flatten_dict(in_dict, prefix=''):
    new_dict = {}
    for k in in_dict.keys():
        v = in_dict[k]
        if type(v) is dict:
            new_prefix = prefix + '.' + k if prefix else k
            new_dict.update(flatten_dict(v, prefix=new_prefix))

        else:
            new_k_name = prefix + '.' + k if prefix else k
            new_dict[new_k_name] = v
    return new_dict


def get_class(full_name):
    """
        This function takes module and class name to import module and gets the object to the class
    """
    try:
        module_path, class_name = full_name.rsplit('.', 1)
        try:
            module = import_module(module_path)
        except ImportError:
            module = import_module("protofiles." + module_path)
        return getattr(module, class_name)
    except (ImportError, AttributeError) as e:
        raise ImportError(full_name)


def print_subscribe_status(topic, status_code, status_message):
    logger.debug('subscribe_status: Topic contents...')
    logger.debug(f"Topic: {topic}, Status Code: {status_code}, Status Message: {status_message}")
    if status_code == 0:
        logger.debug(f"Successfully subscribed for {topic}")
    else:
        logger.error(f"Unsuccessful subscription for {topic} as the status code is {status_code} with status message "
                     f"{status_message}")


def print_publish_status(topic, status_code, status_message):
    logger.debug('publish_status: Topic contents...')
    logger.debug(f"Topic: {topic}, Status Code: {status_code}, Status Message: {status_message}")
    if status_code == 0:
        logger.debug(f"Successfully published for {topic}")
    else:
        logger.error(f"Unsuccessful publish for {topic} as the status code is {status_code} with status message "
                     f"{status_message}")
