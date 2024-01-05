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

        socket.emit("set_env", localStorage.getItem("utransportConfig"))
        socket.emit("set_mcu_config", localStorage.getItem("ip_local"), localStorage.getItem("ip_multicast"))
        socket.emit("set_zenoh_router_ip", localStorage.getItem("zenoh_router_ip"))
        if (segment.includes('configuration')) {
            document.getElementById("localip").value = localStorage.getItem("ip_local")
            document.getElementById("multicastip").value = localStorage.getItem("ip_multicast")
            document.getElementById("zenohrouterip").value = localStorage.getItem("zenoh_router_ip")

        }


        socket.emit('get-info', { "segment": segment })

        if (segment.includes('mockservice')) {
            getMockServices()
        }


    });

    socket.on('onError', function (errormessage) {
        onPubSubError(errormessage)
    });

    socket.on('publish_callback_success', function (res) {
        onPubCallBackSuccess(res)
    });

    socket.on('rpc_dashboard_data_returned', function (res) {
        if (document.getElementById("table_rpc")) {
            setDataOnPageLoad(res);
        }
    });

    socket.on('pubsub_dashboard_data_returned', function (res) {
        if (document.getElementById("table_pub_sub")) {
            setPubSubDataOnPageLoad(res);
        }
    });

    socket.on('publish_callback_fail', function (res) {
        onPubCallBackFail(res)
    });
    socket.on('close_dialog', function () {
        hideSpinner()
    });

    socket.on('sendrpc_callback', function (res) {
        onSendRPCCallBack(res)
    });

    socket.on('sendrpc_response_callback', function (res) {
        hideSpinner()
        onSendRPCResponseCallBack(res)
    });

    socket.on('proxy_configuration_callback', function (json_proxy_data) {
        console.log("Proxy configuration", json_proxy_data)
    });

    socket.on('proxy_status_callback', function (is_proxy_enable) {
        console.log("Proxy Status", is_proxy_enable)
    });

    socket.on('auto_generate_vin_callback', function (random_vin_no) {
        console.log("Random VIN Generated", random_vin_no)
    });

    socket.on('send_generated_vin_callback', function (generated_vin_no) {
        console.log("Generated Random VIN No sent", generated_vin_no)
    });

    socket.on('set-info', function (json) {
        if (json['segment'].includes('proxy')) {
            document.getElementById("url").value = localStorage.getItem("url");
            document.getElementById("vinV").value = localStorage.getItem("vin");
            isHttpEnable = false
            if (localStorage.getItem("http_enable") == 'true')
                isHttpEnable = true
            document.getElementById("customSwitches").checked = isHttpEnable

        }


    });
    socket.on('onException', function (ex) {
        onPubException(ex)
    });

    socket.on('onSendRPCException', function (ex) {
        onSendRPCException(ex)
    });



    socket.on('disconnect', function () {
        socket = null
        //        localStorage.clear();

        console.log("socket-io client is disconnected");
    });

    socket.on('subscribe_callback_success', function (msg) {
        hideSpinner();
        onSubCallbackSuccess(msg);
    });
    socket.on('someip_all_subscribe_callback_success', function (msg) {
        hideSpinner();
        onSubCallbackSuccessSomeIPAll(msg);
    });
    socket.on('subscribe_callback_fail', function (msg) {
        hideSpinner();
        onSubCallbackFail(msg);
    });

    socket.on('subscribe_yaml_callback', function (msg) {
        subscribe_yaml_callback(msg);
    });


    socket.on('subscribe_yaml_success', function (msg) {
        hideSpinner()
        subscribe_yaml_success(msg);
    });

    socket.on('subscribe_yaml_error', function (error) {
        hideSpinner()
        subscribe_yaml_error(error);
    });

    socket.on('unsubscribe_yaml_callback', function (msg) {
        hideSpinner()
        unsubscribe_yaml_callback(msg);
    });

    socket.on('subscribe_signals_callback', function (msg) {
        subscribe_signals_callback(msg);
    });

    socket.on('start_service_callback', function (j) {
        //hideSpinner()
        refreshMockServiceStatus(j, false);

    });
    socket.on('installApkCallback', function (j) {
        //hideSpinner()
        refreshApkStatus(j);

    });

    socket.on('subscribe_signals_success', function (msg) {
        hideSpinner()
        subscribe_signals_success(msg);
    });

    socket.on('subscribe_signals_error', function (error) {
        hideSpinner()
        subscribe_signals_error(error);
    });

    socket.on('unsubscribe_signals_callback', function (msg) {
        hideSpinner()
        unsubscribe_signals_callback(msg);
    });

    socket.on('onTopicUpdate', function (json_res) {
        onTopicUpdate(json_res.json_data, json_res.original_json_data, json_res.topic)
    });

    socket.on('onTopicUpdateSomeIP', function (json_res) {
        onTopicUpdateSomeIP(json_res.json_data, json_res.original_json_data, json_res.topic, json_res.port, json_res.destport)
    });
    socket.on('onTopicUpdateSomeIP_All', function (json_res) {
        onTopicUpdateSomeIP_All(json_res.json_data, json_res.original_json_data, json_res.topic, json_res.port, json_res.destport)
    });
    socket.on('onSubException', function (ex) {
        hideSpinner();
        onSubException(ex)
    });


    socket.on('pubsub_performance_response_callback', function () {
        hideSpinner();
        onPubSubPerformanceCallback()
    });

    socket.on('cpuram_performance_response_callback', function () {
        hideSpinner();
        onCpuRamPerformanceCallback()
    });

    socket.on('cpuload_performance_response_callback', function () {
        hideSpinner();
        onCpuLoadPerformanceCallback()
    });

    socket.on('vin_callback', function () {
        onVINCallback()
    });

    socket.on('exception_callback', function () {
        hideSpinner()
    })

    socket.on('rpc_performance_response_callback', function () {
        hideSpinner();
        onRpcPerformanceCallback()
    });

    socket.on('file_data_callback', function (data) {
        convert_callback(data)
    });

    socket.on('pubsubCmd_callback', function (data) {
        console.log("****pubsubCmd_callback***")
        pubsubCmd_callback(data)
    });

    socket.on('pubsubcpuram_callback', function (data) {
        pubsubcpuram_callback(data)
    });

    socket.on('rpccmd_callback', function (data) {
        rpc_cmd_callback(data)
    });

    socket.on('rpccpuram_callback', function (data) {
        rpc_cpuram_callback(data)
    });

    socket.on('azure_certificate_callback', function () {
        hideSpinner();
    });

    socket.on('playground_output', function (data) {
        hideSpinner();
        playground_output(data)
    });


    socket.on('publish_some_ip_status', function () {
        hideSpinner();
    });


};

function showSpinner() {
    document.getElementById('modalspinner').hidden = false
}

function hideSpinner() {
    document.getElementById('modalspinner').hidden = true
}
function showSpinnerPublishAll() {
    document.getElementById('modalspinnerAll').hidden = false
}

function hideSpinnerPublishAll() {
    document.getElementById('modalspinnerAll').hidden = true
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
