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

import os
import sys
from uprotocol_vsomeip import helper
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
import time

from flask import request
from flask_socketio import SocketIO

from simulator.ui import create_app
from simulator.ui.config import config_dict
from simulator.ui.utils.socket_utils import SocketUtility
from simulator.utils import constant
from tdk.apis.apis import TdkApis
from tdk.helper import someip_helper
from tdk.helper.transport_configuration import TransportConfiguration

debug = True
get_config_mode = "Debug" if debug else "Production"
app_config = config_dict[get_config_mode.capitalize()]

app = create_app(app_config)

# turn the flask apps into a socketio apps
socketio = SocketIO(app, async_mode='threading')

is_reset = True
transport_config = TransportConfiguration()
tdk_apis = TdkApis(transport_config)

socket_utility = SocketUtility(socketio, transport_config, tdk_apis)


@socketio.on(constant.API_SET_UTRANSPORT, namespace=constant.NAMESPACE)
def set_transport(selected_utransport):
    print(selected_utransport.upper())
    transport_config.set_transport(selected_utransport.upper())
    tdk_apis.refresh_transport(transport_config)


@socketio.on(constant.API_SET_SOMEIP_CONFIG, namespace=constant.NAMESPACE)
def set_someip_config(localip, multicastip,is_someip_serializer_enabled=False):
    print(f"set set_someip_config called {localip}, {multicastip}")
    someip_helper.someip_entity = someip_helper.temp_someip_entity
    someip_helper.temp_someip_entity = []
    someip_helper.is_serializer_enabled=is_someip_serializer_enabled
    helper.is_serializer_enabled =is_someip_serializer_enabled
    transport_config.set_someip_config(localip, multicastip)
    tdk_apis.refresh_transport(transport_config)
    time.sleep(0.5)
    socketio.emit(
        constant.CALLBACK_ON_SET_TRANSPORT,
        "",
        namespace=constant.NAMESPACE,
    )


@socketio.on(constant.API_SET_ZENOH_CONFIG, namespace=constant.NAMESPACE)
def set_zenoh_config(routerip, port):
    print(f"set set_zenoh_config called {routerip}, {port}")
    transport_config.set_zenoh_config(routerip, port)
    tdk_apis.refresh_transport(transport_config)
    time.sleep(0.5)
    socketio.emit(
        constant.CALLBACK_ON_SET_TRANSPORT,
        "",
        namespace=constant.NAMESPACE,
    )


@socketio.on(constant.API_SUBSCRIBE, namespace=constant.NAMESPACE)
def subscribe(json_subscribe):
    print("received subscribe json " + str(json_subscribe))
    app.config["SID"] = request.sid
    set_reset_flag()
    asyncio.run(socket_utility.execute_subscribe(json_subscribe))


@socketio.on(constant.API_SENDRPC, namespace=constant.NAMESPACE)
def sendrpc(json_sendrpc):
    set_reset_flag()
    asyncio.run(socket_utility.execute_send_rpc(json_sendrpc))


@socketio.on(constant.API_PUBLISH, namespace=constant.NAMESPACE)
def publish(json_publish):
    set_reset_flag()
    print("received publish json " + str(json_publish))
    app.config["SID"] = request.sid
    asyncio.run(socket_utility.execute_publish(json_publish))


@socketio.on(constant.API_START_SERVICE, namespace=constant.NAMESPACE)
def start_mock_services(json_service):
    print("start mock services json " + str(json_service))
    set_reset_flag()
    asyncio.run(socket_utility.start_mock_service(json_service))


@socketio.on(constant.API_STOP_ALL_SERVICE, namespace=constant.NAMESPACE)
def stop_all_mock_services():
    print("stop all mock services ")
    set_reset_flag()


@socketio.on(constant.API_CONFIGURE_SOMEIP_SERVICE, namespace=constant.NAMESPACE)
def configure_someip_service(json_service):
    print("configure someip service json " + str(json_service))
    set_reset_flag()
    socket_utility.configure_service_someip(json_service)


@socketio.on(constant.API_RESET, namespace=constant.NAMESPACE)
def reset():
    print('socket reconnected')
    global is_reset
    if is_reset:
        try:
            if os.path.isfile(constant.FILENAME_RPC_LOGGER):
                os.remove(constant.FILENAME_RPC_LOGGER)
            if os.path.isfile(constant.FILENAME_PUBSUB_LOGGER):
                os.remove(constant.FILENAME_PUBSUB_LOGGER)
        except Exception:
            pass


def set_reset_flag():
    global is_reset
    is_reset = False


if __name__ == "__main__":
    # Run the server
    socketio.run(app, allow_unsafe_werkzeug=True,port=5000, debug=debug)
