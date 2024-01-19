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
    if os.path.isfile(CONSTANTS.FILENAME_RPC_LOGGER):
        try:
            with open(CONSTANTS.FILENAME_RPC_LOGGER, 'r') as f:
                lines = f.read()
        except IOError as exc:
            print(exc)
        if len(lines) > 0:
            rpc_Calls = json.loads(lines)
        else:
            rpc_Calls = []
        rpc_Calls.append(json_res)
        lock_rpc.acquire()
        try:
            with open(CONSTANTS.FILENAME_RPC_LOGGER, 'w') as f:
                f.write(json.dumps(rpc_Calls, indent=2))
        except IOError as exc:
            print(exc)
        lock_rpc.release()
    else:
        rpc_Calls = [json_res]
        lock_rpc.acquire()
        try:
            with open(CONSTANTS.FILENAME_RPC_LOGGER, 'w') as fp:
                fp.write(json.dumps(rpc_Calls, indent=2))
        except IOError as exc:
            print(exc)
        lock_rpc.release()

    try:
        with open(CONSTANTS.FILENAME_RPC_LOGGER, 'r') as fp:
            data = fp.read()
            if data:
                socketio.emit(CONSTANTS.CALLBACK_RPCLOGGER, data, namespace=CONSTANTS.NAMESPACE)
    except IOError as exc:
        print(exc)


def save_pub_sub_data(socketio, lock_pubsub, json_res):
    if os.path.isfile(CONSTANTS.FILENAME_PUBSUB_LOGGER):
        try:
            with open(CONSTANTS.FILENAME_PUBSUB_LOGGER, 'r') as f:
                lines = f.read()
        except IOError as exc:
            print(exc)

        if len(lines) > 0:
            pubsubData = json.loads(lines)
        else:
            pubsubData = []
        pubsubData.append(json_res)
        lock_pubsub.acquire()
        try:
            with open(CONSTANTS.FILENAME_PUBSUB_LOGGER, 'w') as f:
                f.write(json.dumps(pubsubData, indent=2))
        except IOError as exc:
            print(exc)
        lock_pubsub.release()
    else:
        pubsubData = [json_res]
        lock_pubsub.acquire()
        try:
            with open(CONSTANTS.FILENAME_PUBSUB_LOGGER, 'w') as fp:
                fp.write(json.dumps(pubsubData, indent=2))
        except IOError as exc:
            print(exc)
        lock_pubsub.release()

    try:
        with open(CONSTANTS.FILENAME_PUBSUB_LOGGER, 'r') as fp:
            data = fp.read()
            if data:
                socketio.emit(CONSTANTS.CALLBACK_PUBSUB_LOGGER, data, namespace=CONSTANTS.NAMESPACE)
    except IOError as exc:
        print(exc)
