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


def save_rpc_data(socketio, lock_rpc, json_res):
    rpc_file = constant.FILENAME_RPC_LOGGER
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
        with open(constant.FILENAME_RPC_LOGGER, 'r') as fp:
            data = fp.read()
            if data:
                # Append square brackets to make it a valid JSON array
                data = f'[{data}]'
                socketio.emit(constant.CALLBACK_RPCLOGGER, data, namespace=constant.NAMESPACE)
    except IOError as exc:
        print(exc)


def save_pub_sub_data(socketio, lock_pubsub, json_res):
    pubsub_file = constant.FILENAME_PUBSUB_LOGGER
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
                socketio.emit(constant.CALLBACK_PUBSUB_LOGGER, data, namespace=constant.NAMESPACE)
    except IOError as exc:
        print(exc)
