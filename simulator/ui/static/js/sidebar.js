/*
 * Copyright (c) 2023 General Motors GTO LLC
 *
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 * SPDX-FileType: SOURCE
 * SPDX-FileCopyrightText: 2023 General Motors GTO LLC
 * SPDX-License-Identifier: Apache-2.0
 */


function setTransport(value) {
    console.log("setTransport called");
    try {
        let selectEnv = document.querySelector('#utransportConfig')
        localStorage.setItem('utransportConfig', value)
        resetViews(selectEnv.value)
        socket.emit("set_utransport", value)

    } catch { }

}

function resetViews(value) {
    console.log("resetview")


    try {
        document.getElementById("space_div").hidden = true
        document.getElementById('device_config_div').hidden = true
        document.getElementById('someip_config_div').hidden = true
        document.getElementById('zenoh_config_div').hidden = true
        document.getElementById('mqtt_config_div').hidden = true
        document.getElementById('vehicle_config_div').hidden = true
        if (value == "SOME/IP") {
            document.getElementById('someip_config_div').hidden = false

        } else if (value == "ZENOH") {
            document.getElementById('zenoh_config_div').hidden = false

        } else if (value == "MQTT") {
            document.getElementById('mqtt_config_div').hidden = false

        } else if (value == "VEHICLE") {
            document.getElementById('vehicle_config_div').hidden = false

        }
        else {
            document.getElementById('device_config_div').hidden = false
            document.getElementById('someip_config_div').hidden = true
            document.getElementById('zenoh_config_div').hidden = true
            document.getElementById('mqtt_config_div').hidden = true
            document.getElementById('vehicle_config_div').hidden = true

        }
    } catch { }

    try {
        console.log("neelam" + isFromRefresh)

        //        if (!isFromRefresh) {
        closebtnClicked()
        //        }
    } catch {
    }
}