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
function saveConfig() {
    if (validateConfig()) {
        if (document.querySelector('#utransportConfig').value == "SOME/IP") {
            localStorage.setItem("ip_local", document.getElementById("localip").value)
            localStorage.setItem("ip_multicast", document.getElementById("multicastip").value)
            console.log('before mci config set')
            socket.emit("set_someip_config", document.getElementById("localip").value, document.getElementById("multicastip").value)
        } else if (document.querySelector('#utransportConfig').value == "ZENOH") {
            localStorage.setItem("zenoh_router_ip", document.getElementById("zenohrouterip").value)
            console.log('before zenoh router ip')
            socket.emit("set_zenoh_config", document.getElementById("zenohrouterip").value)
        }

    }
}
function validateConfig() {
    if (document.querySelector('#utransportConfig').value == "SOME/IP") {
        var localip = document.getElementById("localip").value
        var multicastip = document.getElementById("multicastip").value
        if (localip == "") {
            document.getElementById("localip").style.border = '1px solid #F0B323';
            return false
        } else {
            document.getElementById("localip").style.border = '1px solid #ced4da';
        }
        if (multicastip == "") {
            document.getElementById("multicastip").style.border = '1px solid #F0B323';
            return false
        } else {
            document.getElementById("multicastip").style.border = '1px solid #ced4da';
        }
    } else if (document.querySelector('#utransportConfig').value == "ZENOH") {
        var zenohrouterip = document.getElementById("zenohrouterip").value
        if (zenohrouterip == "") {
            document.getElementById("zenohrouterip").style.border = '1px solid #F0B323';
            return false
        } else {
            document.getElementById("zenohrouterip").style.border = '1px solid #ced4da';
        }
    }
    return true
}


