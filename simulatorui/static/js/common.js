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

var segment = null
var socket = null

if (localStorage.getItem("utransportConfig") == null || localStorage.getItem("utransportConfig") == "" ||
    localStorage.getItem("utransportConfig") == 'undefined') {
    localStorage.setItem("utransportConfig", "BINDER")
}

if (localStorage.getItem("ip_local") == null || localStorage.getItem("ip_local") == "" ||
    localStorage.getItem("ip_local") == 'undefined') {
    localStorage.setItem("ip_local", "172.17.0.1")
}
if (localStorage.getItem("ip_multicast") == null || localStorage.getItem("ip_multicast") == "" ||
    localStorage.getItem("ip_multicast") == 'undefined') {
    localStorage.setItem("ip_multicast", "224.224.224.245")
}
if (localStorage.getItem("zenoh_router_ip") == null || localStorage.getItem("zenoh_router_ip") == "" ||
    localStorage.getItem("zenoh_router_ip") == 'undefined') {
    localStorage.setItem("zenoh_router_ip", "127.0.0.1")
}


document.getElementById("utransportConfig").value = localStorage.getItem("utransportConfig")


function unload() {
    console.log('unload')
    socket.close()
}


function setSocketInitialized(sgmt) {
    segment = sgmt;
    setupAllSockets()


}


function setupAllSockets() {
    if (socket === null) {
        setupSocket()
    }
    else if (!socket.connected) {
        setupSocket()
    }

    setTransport(localStorage.getItem("utransportConfig"))

};

function setupSocket() {

    socket = io.connect('http://' + document.domain + ':' + location.port + '/simulator');

    socket.on('connect', function () {
        console.log('socket-io client connected ' + socket.id)
        transport_value = ''

        socket.emit("set_transport", localStorage.getItem("utransportConfig"))
        socket.emit("set_someip_config", localStorage.getItem("ip_local"), localStorage.getItem("ip_multicast"))
        socket.emit("set_zenoh_config", localStorage.getItem("zenoh_router_ip"))
        if (segment.includes('configuration')) {
            document.getElementById("localip").value = localStorage.getItem("ip_local")
            document.getElementById("multicastip").value = localStorage.getItem("ip_multicast")
            document.getElementById("zenohrouterip").value = localStorage.getItem("zenoh_router_ip")

        }

//        socket.emit('get-info', { "segment": segment })

        if (segment.includes('mockservice')) {
            getMockServices()
        }


    });


};

function showSpinner() {
    document.getElementById('modalspinner').hidden = false
}

function hideSpinner() {
    document.getElementById('modalspinner').hidden = true
}


function createspan(text, isSuccess, isBold, id) {
    var span = document.createElement('span');
    span.style.wordWrap = "break-word"
    if (isBold) {
        span.style.fontWeight = "bold"
    }
    if (isSuccess) {
        span.setAttribute("class", "logs-success");
        localStorage.getItem('th') === 'light' ? span.classList.add('logs-success-light') : ''
    }
    else
        span.setAttribute("class", "logs-error");
    span.innerText = text
    try {
        document.getElementById(id).appendChild(span);
    } catch { }

}

function removeAllChildNodes(parent) {
    while (parent.firstChild) {
        parent.removeChild(parent.firstChild);
    }
}
