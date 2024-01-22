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


import os

from flask import request
from flask_socketio import SocketIO

import simulator.utils.constant as CONSTANTS
from simulator.core.transport_layer import TransportLayer
from simulator.ui import create_app
from simulator.ui.config import config_dict
from simulator.ui.utils.socket_utils import SocketUtility

debug = False
get_config_mode = 'Debug' if debug else 'Production'
app_config = config_dict[get_config_mode.capitalize()]

app = create_app(app_config)

# turn the flask apps into a socketio apps
socketio = SocketIO(app)

is_reset = True

transport_layer = TransportLayer()
socket_utility = SocketUtility(socketio, request, transport_layer)


@socketio.on(CONSTANTS.API_SET_UTRANSPORT, namespace=CONSTANTS.NAMESPACE)
def set_transport(selected_utransport):
    transport_layer.set_utransport(selected_utransport.upper())


@socketio.on(CONSTANTS.API_SET_SOMEIP_CONFIG, namespace=CONSTANTS.NAMESPACE)
def set_someip_config(localip, multicastip):
    pass


@socketio.on(CONSTANTS.API_SET_ZENOH_CONFIG, namespace=CONSTANTS.NAMESPACE)
def set_zenoh_config(routerip, port):
    transport_layer.update_zenoh_instance(routerip, port)


@socketio.on(CONSTANTS.API_SUBSCRIBE, namespace=CONSTANTS.NAMESPACE)
def subscribe(json_subscribe):
    print('received subscribe json ' + str(json_subscribe))
    app.config['SID'] = request.sid
    set_reset_flag()
    socket_utility.execute_subscribe(json_subscribe)


@socketio.on(CONSTANTS.API_SENDRPC, namespace=CONSTANTS.NAMESPACE)
def sendrpc(json_sendrpc):
    print('received rpc json ' + str(json_sendrpc))
    set_reset_flag()
    socket_utility.execute_send_rpc(json_sendrpc)


@socketio.on(CONSTANTS.API_PUBLISH, namespace=CONSTANTS.NAMESPACE)
def publish(json_publish):
    set_reset_flag()
    print('received publish json ' + str(json_publish))
    app.config['SID'] = request.sid
    socket_utility.execute_publish(json_publish)


@socketio.on(CONSTANTS.API_START_SERVICE, namespace=CONSTANTS.NAMESPACE)
def start_mock_services(json_service):
    print('start mock services json ' + str(json_service))
    set_reset_flag()
    socket_utility.start_mock_service(json_service)


@socketio.on(CONSTANTS.API_STOP_ALL_SERVICE, namespace=CONSTANTS.NAMESPACE)
def stop_all_mock_services():
    print('stop all mock services ')
    set_reset_flag()


@socketio.on(CONSTANTS.API_RESET, namespace=CONSTANTS.NAMESPACE)
def reset():
    global is_reset
    if is_reset:
        print('reset called')
        if os.path.isfile(CONSTANTS.FILENAME_RPC_LOGGER):
            os.remove(CONSTANTS.FILENAME_RPC_LOGGER)
        if os.path.isfile(CONSTANTS.FILENAME_PUBSUB_LOGGER):
            os.remove(CONSTANTS.FILENAME_PUBSUB_LOGGER)
        if os.path.isfile(CONSTANTS.FILENAME_SERVICE_RUNNING_STATUS):
            os.remove(CONSTANTS.FILENAME_SERVICE_RUNNING_STATUS)


def set_reset_flag():
    global is_reset
    is_reset = False


if __name__ == '__main__':
    # Run the server
    socketio.run(app, allow_unsafe_werkzeug=True, debug=debug)
