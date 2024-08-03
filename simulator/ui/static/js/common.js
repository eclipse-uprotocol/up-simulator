/*
SPDX-FileCopyrightText: 2024 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
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
    localStorage.setItem("zenoh_router_ip", "10.0.0.33")
}
if (localStorage.getItem("zenoh_router_port") == null || localStorage.getItem("zenoh_router_port") == "" ||
    localStorage.getItem("zenoh_router_port") == 'undefined') {
    localStorage.setItem("zenoh_router_port", "9090")
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

};

function setupSocket() {

    socket = io.connect('http://' + document.domain + ':' + location.port + '/simulator');

    socket.on('connect', function () {
        console.log('socket-io client connected ' + socket.id)
        transport_value = ''

        socket.emit("set_transport", localStorage.getItem("utransportConfig"))

        if (segment.includes('configuration')) {
            document.getElementById("localip").value = localStorage.getItem("ip_local")
            document.getElementById("multicastip").value = localStorage.getItem("ip_multicast")
            document.getElementById("zenohrouterip").value = localStorage.getItem("zenoh_router_ip")
            document.getElementById("zenohrouterport").value = localStorage.getItem("zenoh_router_port")

        }
        socket.emit('reset')
        if (segment.includes('mockservice')) {
            getMockServices()
        }
        if (segment.includes('configuration')) {
            getConfigurationMockServices()
        }


    });
    socket.on('start_service_callback', function (j) {
        refreshMockServiceStatus(j.entity, j.status, false);

    });
    socket.on('configure_service_someip_callback', function (j) {
        refreshSomeipServiceConfigureStatus(j.entity, j.status, false);
    });
    socket.on('sendrpc_callback', function (res) {
        onSendRPCCallBack(res)
    });

    socket.on('rpc_logger_callback', function (res) {
        if (document.getElementById("table_rpc")) {
            setDataOnPageLoad(res);
        }
    });
    socket.on('onSendRPCException', function (ex) {
        onSendRPCException(ex)
    });

    socket.on('sendrpc_response_callback', function (res) {
        hideSpinner()
        onSendRPCResponseCallBack(res)
    });

    socket.on('subscribe_callback_success', function (msg) {
        hideSpinner();
        onSubCallbackSuccess(msg);
    });
    socket.on('onSubException', function (ex) {
        hideSpinner();
        onSubException(ex)
    });
    socket.on('subscribe_callback_fail', function (msg) {
        hideSpinner();
        onSubCallbackFail(msg);
    });
    socket.on('onError', function (errormessage) {
        onPubSubError(errormessage)
    });
    socket.on('pub_sub_logger_callback', function (res) {
        hideSpinner()

        if (document.getElementById("table_pub_sub")) {
            setPubSubDataOnPageLoad(res);
        }

    });
    socket.on('publish_callback_success', function (res) {

        onPubCallBackSuccess(res)

    });
    socket.on('publish_callback_fail', function (res) {
        onPubCallBackFail(res)
    });

    socket.on('onPubException', function (ex) {
        onPubException(ex)
    });
    socket.on('onTopicUpdate', function (json_res) {
     hideSpinner()
        onTopicUpdate(json_res.json_data, json_res.original_json_data, json_res.topic)
    });

    socket.on('onSetTransport', function (json_res) {
        hideSpinner()
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
