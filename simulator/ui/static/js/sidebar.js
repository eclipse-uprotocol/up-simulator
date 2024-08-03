/*
SPDX-FileCopyrightText: 2024 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
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
        document.getElementById("configservicesdialog").hidden = true
        document.getElementById("someip_save").hidden = true
        document.getElementById("register_ve_config").classList.remove("config-someip");
        document.getElementById("register_ve_config").classList.add("config-firstRow");
        if (value == "SOME/IP") {
            document.getElementById('someip_config_div').hidden = false
            document.getElementById("configservicesdialog").hidden = false
            document.getElementById("someip_save").hidden = false
            document.getElementById("register_ve_config").classList.remove("config-firstRow");
            document.getElementById("register_ve_config").classList.add("config-someip");

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
        closebtnClicked()
    } catch {
    }
}

// Function to initialize the select element with the saved value
function initializeSelect() {
    // Retrieve the previously saved value
    const savedValue = localStorage.getItem('utransportConfig');

    // Get the select element
    const selectElement = document.getElementById('utransportConfig');

    // Set the saved value or default to the first option if not found
    if (savedValue && selectElement.querySelector(`option[value="${savedValue}"]`)) {
        selectElement.value = savedValue;
        setTransport(savedValue)
    } else {
        // Optionally handle the case where savedValue is not found or is invalid
        selectElement.value = 'BINDER';  // Default value if no valid saved value
    }
}
// Initialize the select element when the page loads
window.onload = initializeSelect;