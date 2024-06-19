/*
SPDX-FileCopyrightText: 2024 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
*/

function saveConfig() {
    if (validateConfig()) {
        if (document.querySelector('#utransportConfig').value == "SOME/IP") {
            showSpinner()
            localStorage.setItem("ip_local", document.getElementById("localip").value)
            localStorage.setItem("ip_multicast", document.getElementById("multicastip").value)
            socket.emit("set_someip_config", document.getElementById("localip").value, document.getElementById("multicastip").value)
        } else if (document.querySelector('#utransportConfig').value == "ZENOH") {
            showSpinner()
            localStorage.setItem("zenoh_router_ip", document.getElementById("zenohrouterip").value)
            localStorage.setItem("zenoh_router_port", document.getElementById("zenohrouterport").value)
            console.log(document.getElementById("zenohrouterport").value)
            socket.emit("set_zenoh_config", document.getElementById("zenohrouterip").value, document.getElementById("zenohrouterport").value)
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
        var zenohrouterport = document.getElementById("zenohrouterport").value
        if (zenohrouterport == "") {
            document.getElementById("zenohrouterport").style.border = '1px solid #F0B323';
            return false
        } else {
            document.getElementById("zenohrouterport").style.border = '1px solid #ced4da';
        }
    }
    return true
}
function onSearchMock() {
    var input, filter, ul, li, a, i, txtValue;
    searchinput = document.getElementById("searchservice");
    filter = searchinput.value.toUpperCase();
    ul = document.getElementById("tableService");
    li = ul.getElementsByTagName("li");
    for (i = 0; i < li.length; i++) {
        a = li[i].getElementsByTagName("a")[0];
        txtValue = a.textContent || a.innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
            li[i].style.display = "";
        } else {
            li[i].style.display = "none";
        }
    }
}

function getConfigurationMockServices() {
    fetch("/getmockservices?env=Someip&transport="+localStorage.getItem("utransportConfig"))
        .then((res) => res.json())
        .then((data) => {
            if (data.result) {
                console.log(data);
                document.getElementById('configservicesdialog').setAttribute("style", "display:block")
                design_config_mock_services_list_layout(data)
            } else {
                document.getElementById('configservicesdialog').setAttribute("style", "display:none")
            }

        })
}
function design_config_mock_services_list_layout(data) {
    removeAllChildNodes(document.getElementById('tableService'))
    var service_status = document.getElementById('box-content');
    let running_services = data.running

    for (let i in data.pkgs_mock) {
        document.getElementById('tableService').appendChild(create_config_ui_for_service(data.pkgs_mock, i))
        for (let k in running_services) {

            if (running_services[k] == data.pkgs_mock[i].entity) {
                service_status.style.display = "none";
                design_someip_service_config_layout(data.pkgs_mock[i].name, data.pkgs_mock[i].entity, "Loading")
                refreshSomeipServiceConfigureStatus(data.pkgs_mock[i].entity, true, true)
                document.getElementById("cbSomeIp" + data.pkgs_mock[i].entity).checked = true
                break;
            }
        }


    }
}
const someip_box_content_list = []

function create_config_ui_for_service(pkgs, i) {
    let input = document.createElement('input')
    let litag = document.createElement('li')
    let divtag = document.createElement('div')
    let atag = document.createElement('a')
    atag.setAttribute("class", "atagclass")
    input.setAttribute("type", "checkbox")
    input.setAttribute("id", "cbSomeIp" + pkgs[i].entity)
    input.setAttribute('key', pkgs[i].entity)
    input.addEventListener("click", function () {
        var sevice_status = document.getElementById('box-content');
        sevice_status.style.display = "none";
        if (document.getElementById("cbSomeIp" + pkgs[i].entity).checked) {
            design_someip_service_config_layout(pkgs[i].name, pkgs[i].entity, "Loading")
            let json = { "entity": pkgs[i].entity }
            console.log("check json=" + json)
            socket.emit('configure_service_someip', json);

        }
        else {
            console.log("uncheck")
            uncheck_id = document.getElementById(pkgs[i].entity);
            console.log(uncheck_id)
            removeSomeipService(pkgs[i].entity)

        }
    }, false);
    let span = document.createElement('span')
    span.setAttribute("class", "checkmark")
    if (localStorage.getItem('th') === 'light') {
        span.classList.add('checkTick-light')
    } else if (localStorage.getItem('th') === 'dark') {
        span.classList.remove('checkTick-light')
    }
    let label = document.createElement('label')
    label.setAttribute("class", "containercheck")
    if (localStorage.getItem('th') === 'light') {
        label.classList.add('label-light')
    } else if (localStorage.getItem('th') === 'dark') {
        label.classList.remove('label-light')
    }
    label.innerText = pkgs[i].name
    label.style.color = "#FFFF"
    label.style.fontSize = "16px"

    let h6 = document.createElement('h6')
    h6.setAttribute("class", "mb-0")
    if (localStorage.getItem('th') === 'light') {
        h6.classList.add('subText-light')

    } else if (localStorage.getItem('th') === 'dark') {
        h6.classList.remove('subText-light')
    }
    h6.setAttribute("style", "margin-top:.50rem!important;")
    h6.innerText = pkgs[i].entity
    h6.style.color = "#FFFF"
    h6.style.fontSize = "14px"

    litag.setAttribute("style", "display:flex;margin:10px 0px 10px -40px;")
    label.appendChild(input)
    label.appendChild(span)
    label.appendChild(h6)
    atag.appendChild(label)
    litag.appendChild(atag)


    return litag
}
function refreshSomeipServiceConfigureStatus(key, isSuccess, isAlreadyRunning) {
    changeIconId = key + "SomeipMock";
    changeStatus = document.getElementById(key);
    changeStatusIcon = document.getElementById(changeIconId)
    if (changeStatus) {
        if (isSuccess) {
            changeStatus.textContent = "Configured";
            changeStatus.style.color = "green";
        } else {
            changeStatus.textContent = "Error";
            changeStatus.style.color = "red";
        }
    }
    if (changeStatusIcon) {
        //        changeStatusIcon.classList.remove("fa", "fa-refresh", "fa-spin", "statusIcon");
        //        console.log("after remove")
        changeStatusIcon.classList.add("fa", "fa", "fa-solid", "fa-stop", "stopIcon");
    }
}

function design_someip_service_config_layout(name, entity, status) {
    someip_box_content_list.push(entity)
    let div = document.createElement('div')
    div.setAttribute("class", "servicecontent")
    const button = document.createElement('div')

    button.setAttribute("class", "buttonload")
    if (localStorage.getItem('th') === 'light') {
        button.classList.add('buttonload-light')
    } else if (localStorage.getItem('th') === 'dark') {
        button.classList.remove('buttonload-light')
    }

    button.setAttribute("id", "someipbuttonload" + entity)
    if (name.includes("Service")) {
        button.innerHTML = name;
    } else {
        button.innerHTML = name + " Service";
    }
    var icon = document.createElement('i');
    //    icon.className = "fa fa-refresh fa-spin statusIcon";
    icon.className = "fa fa fa-solid fa-stop stopIcon"
    if (localStorage.getItem('th') === 'light') {
        icon.classList.add('icon-light')
    } else if (localStorage.getItem('th') === 'dark') {
        icon.classList.remove('icon-light')
    }
    var iconId = entity + "SomeipMock";
    icon.setAttribute("id", iconId)
    const divElement = document.createElement("div");
    const divicon = document.createElement("div");
    divicon.setAttribute("class", "icon-container");
    divicon.setAttribute("id", "Someipicon" + entity);
    divicon.appendChild(icon);
    divicon.addEventListener('click', () => removeSomeipService(entity))
    divElement.id = entity;
    var styles = {
        "display": "inline-block",
        "width": "30%",
        "font-family": "Overpass,sans-serif,aril",
        "font-style": "normal",
        "font-weight": "700",
        "font-size": "18px",
        "line-height": "150%",
        "color": "#F0B323"
    }
    divElement.textContent = status;
    Object.assign(divElement.style, styles);
    div.appendChild(button);
    document.querySelector(".someipservicedata").hidden = false
    document.querySelector(".someipservicedata").appendChild(button);
    document.querySelector(".someipservicedata").appendChild(divElement);
    document.querySelector(".someipservicedata").appendChild(divicon);
}

function removeSomeipService(id) {
    uncheck_id = document.getElementById(id);
    uncheckIcon_id = document.getElementById("Someipicon" + id);
    uncheckbutton_id = document.getElementById("someipbuttonload" + id);
    document.querySelector(".someipservicedata").removeChild(uncheck_id);
    document.querySelector(".someipservicedata").removeChild(uncheckbutton_id);
    document.querySelector(".someipservicedata").removeChild(uncheckIcon_id);

    activeCheckbox = document.getElementById("cbSomeIp" + id)
    activeCheckbox.checked = false

    fetch("/updatesomeipservicestatus?entity=" + id)
        .then((res) => res.json())
        .then((data) => {
            if (data.result) {

            }
        }).catch((error) => console.log(error));
}

