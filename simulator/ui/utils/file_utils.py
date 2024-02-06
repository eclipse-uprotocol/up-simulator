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

import json
import os

import simulator.utils.constant as CONSTANTS


def save_rpc_data(socketio, lock_rpc, json_res):
    rpc_file = CONSTANTS.FILENAME_RPC_LOGGER
    lock_rpc.acquire()
    try:
        with open(rpc_file, 'a') as f:
            if os.path.getsize(rpc_file) > 0:
                f.write(',')
                f.write('\n')

            f.write(json.dumps(json_res, indent=2))  # Add a newline after each JSON object
    except IOError as exc:
        print(exc)
    finally:
        lock_rpc.release()

    try:
        with open(CONSTANTS.FILENAME_RPC_LOGGER, 'r') as fp:
            data = fp.read()
            if data:
                # Append square brackets to make it a valid JSON array
                data = f'[{data}]'
                socketio.emit(CONSTANTS.CALLBACK_RPCLOGGER, data, namespace=CONSTANTS.NAMESPACE)
    except IOError as exc:
        print(exc)


def save_pub_sub_data(socketio, lock_pubsub, json_res):
    pubsub_file = CONSTANTS.FILENAME_PUBSUB_LOGGER
    lock_pubsub.acquire()
    try:
        with open(pubsub_file, 'a') as f:
            if os.path.getsize(pubsub_file) > 0:
                f.write(',')
                f.write('\n')

            f.write(json.dumps(json_res, indent=2))  # Add a newline after each JSON object
    except IOError as exc:
        print(exc)
    finally:
        lock_pubsub.release()

    try:
        with open(pubsub_file, 'r') as fp:
            data = fp.read()
            if data:
                # Append square brackets to make it a valid JSON array
                data = f'[{data}]'
                socketio.emit(CONSTANTS.CALLBACK_PUBSUB_LOGGER, data, namespace=CONSTANTS.NAMESPACE)
    except IOError as exc:
        print(exc)


