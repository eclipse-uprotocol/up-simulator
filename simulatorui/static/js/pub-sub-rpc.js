function myFunctionpubsub() {
    var input, filter, ul, li, a, i, txtValue;
    searchinput = document.getElementById("searchpubsub");
    filter = searchinput.value.toUpperCase();
    ul = document.getElementById("myULdata");
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
function checkboxclicked(service, pubsub_or_resource) {
    var checkboxpub = document.getElementById("cb" + service.name);
    var sevice_status = document.getElementById('box-content');

    var div_content = document.getElementById('div' + service.name);

    if (checkboxpub.checked) {
        sevice_status.style.display = "none";
        div_content.style.display = 'block'
        if (pubsub_or_resource == "pubsub") {
            for (var i = 0; i < service.pubsub.length; i++) {
                var idName = "cb" + service.name + service.pubsub[i];
                var pubsubRadioBtn = document.getElementById(idName);
                pubsubRadioBtn.checked = false;
            }
        }
        if (pubsub_or_resource == "resource") {
            for (var i = 0; i < service.resource.length; i++) {
                var idName = "cb" + service.name + service.resource[i];
                var resourceRadioBtn = document.getElementById(idName);
                resourceRadioBtn.checked = false;
            }
        }

        var modallg = document.getElementById("modal-lgss")
        var bottomcontent = document.getElementById("bottomcontent")
        var logbox = document.getElementById("logbox")

        bottomcontent.style.display = "none"
        modallg.style.display = "none"
        logbox.style.display = "none"
        //        logboxdata.style.display = "none"
        const allCB = document.querySelectorAll('input[type="checkbox"]')

        allCB.forEach(checkbox => {
            if (checkbox.id != 'cbTheme') {
                if (checkbox.checked && checkboxpub !== checkbox) {
                    checkbox.checked = false;
                    document.getElementById('div' + checkbox.id.substr(2)).style.display = "none"
                }
            }

        })
    }

    else {
        div_content.style.display = "none"
        closebtnClicked()
    }
}


function onPubSubError(errormessage) {
    createspan("Received error " + errormessage + "\n\n", false, true, "logsdesc")
    hideSpinner()
    alert = document.getElementById('error')
    alert.setAttribute("style", "display:block")
    alert.innerText = errormessage
    setTimeout(function () {
        try {
            let divh = document.getElementById("uidesignbox").clientHeight
            let footerdivh = document.getElementById("footer").clientHeight
            if (divh + footerdivh + alert.clientHeight > 0) {
                document.getElementById("logsbox").style.height = (divh + footerdivh + alert.clientHeight) + 'px';
            }
        } catch { }
    }, 300);
}

function onPubCallBackSuccess(res) {
    createspan(res['msg'] + "\n\n", true, true, "logsdesc")
    if (res.hasOwnProperty('data')) {
        createspan(JSON.stringify(res['data'], null, 2) + "\n\n", true, false, "logsdesc")
    }
    hideSpinner()
}

function onPubCallBackFail(res) {
    createspan(res['msg'] + "\n", false, true, "logsdesc")
    hideSpinner()
}

function onSendRPCCallBack(res) {
    if (res.hasOwnProperty('data')) {
        createspan(res['msg'] + "\n", true, true, "logsdesc")
        createspan(JSON.stringify(res['data'], null, 2) + "\n\n", true, false, "logsdesc")
    } else {
        createspan(res['msg'] + "\n\n", true, true, "logsdesc")
    }
    hideSpinner()
}

function onSendRPCResponseCallBack(res) {
    createspan("Received RPC Response from Vehicle Service" + "\n", true, true, "logsdesc")
    createspan(JSON.stringify(res, null, 2) + "\n\n", true, false, "logsdesc")
    if (segment.includes("configuration")) {
        if (res.hasOwnProperty('message')) {
            var status = document.getElementById("updatenode_status")

            status.innerText = "Response - " + res.message
            if (res.message.includes('uccess'))
                status.style.color = 'green'
            else
                status.style.color = 'red'
        }
    }
}

function onPubException(ex) {
    createspan("Received exception from publish method" + "\n", false, true, "logsdesc")
    createspan(ex + "\n\n", false, false, "logsdesc")
    hideSpinner()
}

function onSendRPCException(ex) {
    createspan("Received exception from RPC method" + "\n", false, true, "logsdesc")
    createspan(ex + "\n\n", false, false, "logsdesc")
    hideSpinner()
}

function onSubCallbackSuccess(msg) {
    createspan(msg + "\n\n", true, true, "logsdesc")
}

function onSubCallbackFail(msg) {
    createspan(msg + "\n\n", false, true, "logsdesc")
}

function onTopicUpdateSomeIP(json_proto, json_proto_original, topic, port, destport) {
    console.log("someip=" + selectedTopic)
    if (topic == selectedTopic) {
        if (JSON.stringify(json_proto, null, 2).length > 2) {
            createspan("Received topic update from SOME/IP on port " + port + ", dest. port " + destport + "\n", true, true, "logsdesc")
            createspan(JSON.stringify(json_proto_original, null, 2) + "\n\n", true, false, "logsdesc")
        }
        updateui_ontopicupdate(json_proto)

    }
}

function onTopicUpdate(json_proto, json_proto_original, topic) {
    if (JSON.stringify(json_proto, null, 2).length > 2) {
        if (topic == selectedTopic) {
            createspan("Received topic update from Bus Service" + "\n", true, true, "logsdesc")
            createspan(JSON.stringify(json_proto_original, null, 2) + "\n\n", true, false, "logsdesc")
            updateui_ontopicupdate(json_proto)
        }
    }
}

function updateui_ontopicupdate(json_proto) {

    setvalues(json_proto, 'false')

}

function onSubException(ex) {
    createspan("Received Exception from subscribe method" + "\n\n", false, true, "logsdesc")
    createspan(ex + "\n\n", false, false, "logsdesc")
}
function onbackClicked() {
    var backBtn = document.getElementById('back_pub')
    servicename = backBtn.getAttribute("servicename")
    showConfigDialog(false, servicename)

}
function onRbChanged(label, service, typeTab) {

    if (typeTab == "Publish") {
        if (localStorage.getItem("utransportConfig") == "SOME/IP" || localStorage.getItem("utransportConfig") == "ZENOH") {
            document.getElementById("sub_utransport").hidden = false
        } else {
            document.getElementById("sub_utransport").hidden = true
        }
    }
    setupAllSockets()
    alert = document.getElementById('error')
    alert.setAttribute("style", "display:none")
    setvalues({}, 'true')
    if (typeTab != "AddRPC") {
        var backBtn = document.getElementById('back_pub')
        back_pub.setAttribute("servicename", service['name'])
        removeAllChildNodes(document.getElementById("logsdesc"))
    }

    var executebtn = document.getElementById('execute')
    executebtn.innerText = typeTab
    executebtn.setAttribute("class", "btn btn-primary")
    fetch("/getuiconfiguration?resource=" + label + "&service=" + JSON.stringify(service))
        .then((res) => res.json())
        .then((data) => {
            if (JSON.stringify(data).length > 2) {
                var servicename = '';
                if (service.hasOwnProperty('servicename'))
                    servicename = service.servicename
                design_layout(data, label, servicename)
                if (typeTab != "AddRPC") {

                    showConfigDialog(true, service.name)
                } else {

                    $('#modal-lg').modal().show();
                }
            }
        })
        .catch((error) => console.log(error));
}

function showConfigDialog(isShow, servicename) {

    var divservice = document.getElementById("div" + servicename)

    var configuration = document.getElementById("pubrpcheader")


    var modallg = document.getElementById("modal-lgss")
    var bottomcontent = document.getElementById("bottomcontent")
    var logbox = document.getElementById("logbox")


    if (isShow) {
        bottomcontent.style.display = "block"
        modallg.style.display = "block"
        divservice.style.display = "none"
        logbox.style.display = "block"

        configuration.style.display = "block"

    } else {
        bottomcontent.style.display = "none"
        modallg.style.display = "none"
        divservice.style.display = "block"
        logbox.style.display = "none"

        configuration.style.display = "none"

    }


}
selectedTopic = ''
function onConfigClick(rb) {
    if (rb.checked) {
        setvalues({}, 'true')
        selectedTopic = rb.getAttribute("topic")
        if (localStorage.getItem("utransportConfig") in ["BINDER", "VEHICLE"]) {
            executesubscribe(rb.getAttribute("topic"))
        }


        if (rb.hasAttribute("rpc")) {
            document.getElementById("pubrpcheader").innerText = rb.getAttribute("rpc")
        } else {
            document.getElementById("pubrpcheader").innerText = "Configuration"
        }

    }
}
$("#modal-lg").on("show.bs.modal", function () {
    if (document.getElementById('execute').innerText != 'AddRPC') {
        removeAllChildNodes(document.getElementById("logsdesc"))
        setTimeout(function () {
            divh = document.getElementById("uidesignbox").clientHeight
            footerdivh = document.getElementById("footer").clientHeight
            if (divh + footerdivh > 0) {
                document.getElementById("logsbox").style.height = (divh + footerdivh) + 'px';
            }
        }, 300);
    }

});

function clearLog() {
    removeAllChildNodes(document.getElementById("logsdesc"))
}

function setvalues(json_proto, clearValues) {
    //logic for time
    keys = Object.keys(json_proto);
    for (key in keys) {
        if (keys[key].includes(".hours")) {
            var prefixkey = keys[key].split(".hours")[0]
            var hours = ('0' + json_proto[keys[key]]).slice(-2)
            var min = ('0' + json_proto[prefixkey + ".minutes"]).slice(-2)
            var sec = ('0' + json_proto[prefixkey + ".seconds"]).slice(-2)
            json_proto[prefixkey] = hours + ":" + min + ":" + sec
            delete json_proto[keys[key]]
            delete json_proto[prefixkey + ".minutes"]
            delete json_proto[prefixkey + ".seconds"]
            delete json_proto[prefixkey + ".nanos"]
        }
    }
    console.log("updated json" + JSON.stringify(json_proto))

    var inputs = document.getElementById('uidesign').getElementsByTagName('input');
    var selects = document.getElementById('uidesign').getElementsByTagName('select');
    for (var j = 0; j < selects.length; ++j) {
        var previous_state = selects[j].disabled
        selects[j].disabled = false
        var optionsarr = selects[j].options
        if (selects[j].labels[0].hasAttribute('property')) {
            if (json_proto.hasOwnProperty(selects[j].labels[0].getAttribute('property'))) {
                for (var k = 0; k < optionsarr.length; ++k) {
                    if (optionsarr[k].outerText == json_proto[selects[j].labels[0].getAttribute('property')])
                        selects[j].value = optionsarr[k].value
                }
            } else {
                if (clearValues == 'true')
                    selects[j].value = optionsarr[0].value
            }
            selects[j].disabled = previous_state
        } else {
            if (json_proto.hasOwnProperty(selects[j].labels[0].innerText)) {
                for (k = 0; k < optionsarr.length; ++k) {
                    if (optionsarr[k].outerText == json_proto[selects[j].labels[0].innerText])
                        selects[j].value = optionsarr[k].value
                }
            } else {
                if (clearValues == 'true')
                    selects[j].value = optionsarr[0].value
            }
        }
    }

    for (var index = 0; index < inputs.length; ++index) {

        previous_state = inputs[index].disabled
        inputs[index].disabled = false
        if (inputs[index].attributes[0].nodeName == 'isconfig' && inputs[index].attributes[0].nodeValue == 'yes') {
            if (json_proto.hasOwnProperty(inputs[index].labels[0].innerText)) {
                inputs[index].checked = true

            }

        } else {
            if (inputs[index].labels[0].hasAttribute('property')) {
                if (inputs[index].attributes[1].nodeValue == 'checkbox') {
                    if (json_proto.hasOwnProperty(inputs[index].labels[0].getAttribute('property'))) {
                        inputs[index].checked = json_proto[inputs[index].labels[0].getAttribute('property')]
                    } else {
                        if (clearValues == 'true')
                            inputs[index].checked = false
                    }
                } else if (inputs[index].attributes[1].nodeValue == 'number') {
                    if (json_proto.hasOwnProperty(inputs[index].labels[0].getAttribute('property'))) {
                        inputs[index].valueAsNumber = json_proto[inputs[index].labels[0].getAttribute('property')]
                    } else {
                        if (clearValues == 'true') {
                            inputs[index].valueAsNumber = 0

                        }
                    }
                } else if (inputs[index].attributes[1].nodeValue == 'timetext') {
                    if (json_proto.hasOwnProperty(inputs[index].labels[0].getAttribute('property'))) {
                        inputs[index].value = json_proto[inputs[index].labels[0].getAttribute('property')]
                    } else {
                        if (clearValues == 'true') {
                            inputs[index].value = ''

                        }
                    }
                } else if (inputs[index].attributes[1].nodeValue == 'text') {
                    if (json_proto.hasOwnProperty(inputs[index].labels[0].getAttribute('property'))) {
                        inputs[index].value = json_proto[inputs[index].labels[0].getAttribute('property')]
                    } else {
                        if (clearValues == 'true') {
                            inputs[index].value = ''

                        }
                    }
                }
            } else {
                if (inputs[index].attributes[1].nodeValue == 'checkbox') {
                    if (json_proto.hasOwnProperty(inputs[index].labels[0].innerText)) {
                        inputs[index].checked = json_proto[inputs[index].labels[0].innerText]
                    } else {
                        if (clearValues == 'true')
                            inputs[index].checked = false
                    }
                } else if (inputs[index].attributes[1].nodeValue == 'number') {
                    if (json_proto.hasOwnProperty(inputs[index].labels[0].innerText)) {
                        inputs[index].valueAsNumber = json_proto[inputs[index].labels[0].innerText]
                    } else {
                        if (clearValues == 'true') {
                            inputs[index].valueAsNumber = 0
                        }
                    }
                } else if (inputs[index].attributes[1].nodeValue == 'timetext') {
                    if (json_proto.hasOwnProperty(inputs[index].labels[0].innerText)) {
                        inputs[index].value = json_proto[inputs[index].labels[0].innerText]
                    } else {
                        if (clearValues == 'true') {
                            inputs[index].value = ''
                        }
                    }
                } else if (inputs[index].attributes[1].nodeValue == 'text') {
                    if (json_proto.hasOwnProperty(inputs[index].labels[0].innerText)) {
                        inputs[index].value = json_proto[inputs[index].labels[0].innerText]
                    } else {
                        if (clearValues == 'true') {
                            inputs[index].value = ''
                        }
                    }
                }
            }
        }

        inputs[index].disabled = previous_state

    }
}

function executesubscribe(topic) {
    //connect to the socket server.
    if (topic.length > 0) {
        if (document.getElementById('execute').innerText != 'AddRPC') {
            try {
                if (topic.includes("dynamic_topic")) {
                    topic = topic.replace("dynamic_topic", JSON.parse(data)['name'])
                    selectedTopic = topic
                }
            } catch {
            }
            if (!topic.includes("dynamic_topic")) {
                //uncomment later
                //showSpinner();
                var jsonsubscribe = { "topic": topic.replace("#", "123") }
                socket.emit('subscribe', jsonsubscribe);
            }
        }
    }
}



function callPublishApi(data, topic, serviceclass) {
    if (topic.includes("dynamic_topic")) {
        topic = topic.replace("dynamic_topic", JSON.parse(data)['name'])
        if (localStorage.getItem("utransportConfig") in ["BINDER", "VEHICLE"]) {
            executesubscribe(topic)
        }
        var jsonpublish = { "service_class": serviceclass, "topic": topic, "data": data }
        socket.emit('publish', jsonpublish);
    } else {
        var jsonpublish = { "service_class": serviceclass, "topic": topic, "data": data }
        socket.emit('publish', jsonpublish);
    }
}

function callSendRPCApi(data, methodname, serviceclass, maskField) {
    var jsonsendrpc = { "methodname": methodname, "data": data, "serviceclass": serviceclass, "mask": JSON.stringify(maskField), "repeated_keys": JSON.stringify(Object.keys(json_repeated_dict)) }
    socket.emit('sendrpc', jsonsendrpc);

}
function getAllDropDownValues(selects, json_data) {
    for (j = 0; j < selects.length; ++j) {
        if (selects[j].disabled == false) {
            if (selects[j].labels[0].hasAttribute('rpcproperty')) {
                json_data[selects[j].labels[0].getAttribute('rpcproperty')] = selects[j].options[selects[j].selectedIndex].innerText;
            } else {
                if (selects[j].labels[0].hasAttribute('property'))
                    json_data[selects[j].labels[0].getAttribute('property')] = selects[j].options[selects[j].selectedIndex].innerText;
                else
                    json_data[selects[j].labels[0].innerText] = selects[j].options[selects[j].selectedIndex].innerText;
            }
        }
    }
}

function getAllUiValues(input, json_data) {
    for (index = 0; index < inputs.length; ++index) {
        // deal with inputs[index] element.
        if (inputs[index].hasAttribute('isconfig') && inputs[index].getAttribute('isconfig') == 'yes') {
            if (inputs[index].checked) {
                if (inputs[index].hasAttribute('resource_name')) {
                    json_data['resource_name'] = inputs[index].getAttribute('resource_name')
                }
                if (inputs[index].id != 'N') {
                    if ((inputs[index].id).includes('.')) {
                        json_data['name'] = inputs[index].id

                        if (inputs[index].hasAttribute('name_key')) {
                            json_data[inputs[index].getAttribute('name_key')] = inputs[index].id
                        } else {
                            json_data[(inputs[index].id).split('.')[0] + ".name"] = inputs[index].id
                        }
                    } else {
                        json_data['name'] = inputs[index].id
                    }
                }
                topic = inputs[index].getAttribute('topic')
                methodname = inputs[index].getAttribute('rpc')
                serviceclass = inputs[index].getAttribute('serviceclass')
            }
        }
        else {
            if (inputs[index].disabled == false) {
                if (inputs[index].labels[0].hasAttribute('rpcproperty')) {

                    if (inputs[index].attributes[1].nodeValue == 'checkbox')
                        json_data[inputs[index].labels[0].getAttribute('rpcproperty')] = inputs[index].checked
                    else if (inputs[index].attributes[1].nodeValue == 'number')
                        json_data[inputs[index].labels[0].getAttribute('rpcproperty')] = inputs[index].valueAsNumber
                    else if (inputs[index].attributes[1].nodeValue == 'text')
                        json_data[inputs[index].labels[0].getAttribute('rpcproperty')] = inputs[index].value
                    else if (inputs[index].attributes[1].nodeValue == 'timetext') {
                        if (inputs[index].value != '') {
                            json_data[inputs[index].labels[0].getAttribute('rpcproperty') + ".hours"] = parseInt(inputs[index].value.split(":")[0])
                            json_data[inputs[index].labels[0].getAttribute('rpcproperty') + ".minutes"] = parseInt(inputs[index].value.split(":")[1])
                            json_data[inputs[index].labels[0].getAttribute('rpcproperty') + ".seconds"] = parseInt(inputs[index].value.split(":")[2]) || 0
                        } else {
                            json_data[inputs[index].labels[0].getAttribute('rpcproperty') + ".hours"] = 0
                            json_data[inputs[index].labels[0].getAttribute('rpcproperty') + ".minutes"] = 0
                            json_data[inputs[index].labels[0].getAttribute('rpcproperty') + ".seconds"] = 0
                        }
                        json_data[inputs[index].labels[0].getAttribute('rpcproperty') + ".nanos"] = 0
                    }



                } else {
                    if (inputs[index].labels[0].hasAttribute('property')) {
                        if (inputs[index].attributes[1].nodeValue == 'checkbox')
                            json_data[inputs[index].labels[0].getAttribute('property')] = inputs[index].checked
                        else if (inputs[index].attributes[1].nodeValue == 'number')
                            json_data[inputs[index].labels[0].getAttribute('property')] = inputs[index].valueAsNumber
                        else if (inputs[index].attributes[1].nodeValue == 'text')
                            json_data[inputs[index].labels[0].getAttribute('property')] = inputs[index].value
                        else if (inputs[index].attributes[1].nodeValue == 'timetext') {
                            if (inputs[index].value != '') {
                                json_data[inputs[index].labels[0].getAttribute('property') + ".hours"] = parseInt(inputs[index].value.split(":")[0])
                                json_data[inputs[index].labels[0].getAttribute('property') + ".minutes"] = parseInt(inputs[index].value.split(":")[1])
                                json_data[inputs[index].labels[0].getAttribute('property') + ".seconds"] = parseInt(inputs[index].value.split(":")[2]) || 0

                            } else {
                                json_data[inputs[index].labels[0].getAttribute('property') + ".hours"] = 0
                                json_data[inputs[index].labels[0].getAttribute('property') + ".minutes"] = 0
                                json_data[inputs[index].labels[0].getAttribute('property') + ".seconds"] = 0

                            }
                            json_data[inputs[index].labels[0].getAttribute('property') + ".nanos"] = 0
                        }

                    } else {
                        if (inputs[index].attributes[1].nodeValue == 'checkbox')
                            json_data[inputs[index].labels[0].innerText] = inputs[index].checked
                        else if (inputs[index].attributes[1].nodeValue == 'number')
                            json_data[inputs[index].labels[0].innerText] = inputs[index].valueAsNumber
                        else if (inputs[index].attributes[1].nodeValue == 'text')
                            json_data[inputs[index].labels[0].innerText] = inputs[index].value
                        else if (inputs[index].attributes[1].nodeValue == 'timetext') {
                            if (inputs[index].value != '') {
                                json_data[inputs[index].labels[0].innerText + ".hours"] = parseInt(inputs[index].value.split(":")[0])
                                json_data[inputs[index].labels[0].innerText + ".minutes"] = parseInt(inputs[index].value.split(":")[1])
                                json_data[inputs[index].labels[0].innerText + ".seconds"] = parseInt(inputs[index].value.split(":")[2]) || 0
                            } else {
                                json_data[inputs[index].labels[0].innerText + ".hours"] = 0
                                json_data[inputs[index].labels[0].innerText + ".minutes"] = 0
                                json_data[inputs[index].labels[0].innerText + ".seconds"] = 0

                            }
                            json_data[inputs[index].labels[0].innerText + ".nanos"] = 0
                        }


                    }
                }
            }
        }
    }
}
var topic = ''
var methodname = ''
var serviceclass = ''

function executePublish_Set(typeButton, json_data) {
    topic = ''
    methodname = ''
    serviceclass = ''
    selects = document.getElementById('uidesign').getElementsByTagName('select');
    getAllDropDownValues(selects, json_data)

    inputs = document.getElementById('uidesign').getElementsByTagName('input');
    getAllUiValues(inputs, json_data)

    json_data = { ...json_data, ...json_repeated_dict }

    console.log("final json ", JSON.stringify(json_data, null, 2))
    if (typeButton == 'RPC') {
        if (['body.access', 'body.cabin_climate', 'body.lighting.interior', 'body.lighting.exterior']
            .includes(serviceclass)) {
            setmaskfield(json_data, methodname, serviceclass, typeButton, topic)
        } else {
            //uncomment later
            //showSpinner();
            callSendRPCApi(JSON.stringify(json_data).replace("#", "123"), methodname, serviceclass, [])
        }
    } else if (typeButton == "PUB") {
        //uncomment later
        //showSpinner();
        callPublishApi(JSON.stringify(json_data).replace("#", "123"), topic.replace("#", "123"), serviceclass)
    } else if (typeButton == 'AddRPC') {
        if (['body.access', 'body.cabin_climate', 'body.lighting.interior', 'body.lighting.exterior']
            .includes(serviceclass)) {
            setmaskfield(json_data, methodname, serviceclass, typeButton, topic)
        } else {
            addRpcToRow(json_data, topic, methodname, serviceclass, [])
            $('#modal-lg').modal('hide');
        }

    }

}
function closeMaskDialog() {
    const dialog = document.querySelector('.dialog');
    dialog.style.display = 'none';
}

function sendRpcFromMask() {
    const dialog = document.querySelector('.dialog');
    const checkedItems = Array.from(document.querySelectorAll('.dialog input[type="checkbox"]:checked'))
        .map(checkbox => checkbox.value);
    dialog.style.display = 'none';
    if (type_button == 'RPC') {
        //uncomment later
        //showSpinner();
        callSendRPCApi(JSON.stringify(rpc_json_data).replace("#", "123"), method_name, service_class, checkedItems)
    } else {
        addRpcToRow(rpc_json_data, per_topic, method_name, service_class, checkedItems)
        $('#modal-lg').modal('hide');
    }
}
var method_name = ''
var service_class = ''
var rpc_json_data
var type_button = ''
var per_topic = ''
function setmaskfield(json_data, methodname, serviceclass, typeButton, topic) {
    rpc_json_data = json_data
    method_name = methodname
    service_class = serviceclass
    type_button = typeButton
    per_topic = topic
    var maskul = document.getElementById("maskul");
    removeAllChildNodes(maskul)
    for (i in json_data) {
        if (i != 'name') {
            const li = document.createElement("li");
            const input = document.createElement("input")
            input.setAttribute("value", i)
            input.setAttribute("name", i)
            input.setAttribute("type", "checkbox")
            input.innerText = i
            li.appendChild(input)
            const label = document.createElement('label');
            label.setAttribute("class", "containercheck")
            label.style.fontSize = '16px';
            const span = document.createElement('span');
            span.setAttribute("class", "checkmark")
            if (localStorage.getItem('th') === 'light') {
                span.classList.add('checkTick-light')
            } else if (localStorage.getItem('th') === 'dark') {
                span.classList.remove('checkTick-light')
            }

            const node = document.createTextNode(i)
            label.appendChild(node)

            label.appendChild(input)
            label.appendChild(span)
            li.appendChild(label)
            maskul.appendChild(li)
        }
    }
    const dialog = document.querySelector('.dialog');
    dialog.style.display = 'block';


}
var publishSavedData = []
function setRangeValues(inputs) {
    if (inputs.value.length > 0 && inputs.valueAsNumber > parseFloat(inputs.max)) {
        inputs.valueAsNumber = parseFloat(inputs.max)
    } else if (inputs.valueAsNumber < parseFloat(inputs.min)) {
        inputs.valueAsNumber = parseFloat(inputs.min)
    }
}
function onRangeBlur(inputs) {
    if (inputs.value.length == 0) {
        inputs.valueAsNumber = parseFloat(inputs.min)
    }
}

function executeSave() {
    var json_data = {}

    executePublish_Set('SAVE', json_data)

}
function execute() {
    var executionvalue = document.getElementById('execute').innerText
    var json_data = {}

    if (executionvalue == 'Publish') {
        executePublish_Set('PUB', json_data)
    } else if (executionvalue == 'Send RPC') {
        executePublish_Set('RPC', json_data)
    } else if (executionvalue == 'AddRPC') {
        document.getElementById("addbtn").disabled = true;
        document.getElementById("submitbtn").disabled = true;
        executePublish_Set('AddRPC', json_data)
    }
}




mask = []


function handleLabelElement(uiDetailsLabel, elLabel) {
    var iDiv = document.createElement('div');
    var hr = document.createElement('hr');
    hr.setAttribute("style", "border-top-color: orange;")
    var p = document.createElement('p');
    p.setAttribute("style", "margin-top:5px; margin-bottom:-15px; font-size:12px;color: orange;")
    p.innerText = uiDetailsLabel.text
    iDiv.appendChild(p)
    iDiv.appendChild(hr)
    elLabel.appendChild(iDiv)
}
function handleRepeatedlement(uiDetailsRepeated, resourceRepeated, elRepeated) {
    console.log("===", "Repeated")
    var iDiv = document.createElement('div');
    iDiv.setAttribute('class', 'form-group')
    iDiv.setAttribute("style", "margin-bottom: 5px;");
    var iInput = document.createElement('button');
    iInput.addEventListener("click", function () {
        console.log("====", "inside repeated")
        console.log("====", uiDetailsRepeated.value)
        console.log("====", uiDetailsRepeated.key)
        design_layout_repeated(uiDetailsRepeated.value, uiDetailsRepeated.key, uiDetailsRepeated.class);
    }, false);
    if (uiDetailsRepeated.hasOwnProperty("readonly") && uiDetailsRepeated.readonly == 'True') {
        iInput.disabled = true;
    }
    iInput.setAttribute("isconfig", "no")
    iInput.innerText = '+'
    iInput.setAttribute("class", "btn btn-primary ")
    iInput.setAttribute("style", "vertical-align:top;background: #3B3B39;border: 1px solid #5EB1F3;border-radius: 2px;color: #5EB1F3;    font-size: 16px;font-weight: 400;line-height: 26px;float:right")
    //    iInput.setAttribute("style", "")
    iInput.setAttribute("data-toggle", "modal");
    iInput.setAttribute("data-target", "#myModal2");
    iInput.setAttribute("id", resourceRepeated + uiDetailsRepeated.key)
    var iLabel = document.createElement('label');
    if (uiDetailsRepeated.hasOwnProperty('rpcproperty'))
        iLabel.setAttribute("rpcproperty", uiDetailsRepeated.rpcproperty)

    if (uiDetailsRepeated.hasOwnProperty('propertyText')) {
        iLabel.setAttribute("property", uiDetailsRepeated.key)
        iLabel.innerText = uiDetailsRepeated.key
    } else {
        iLabel.innerText = uiDetailsRepeated.key
    }
    iLabel.setAttribute("style", "font-size: 16px;width:100%;")
    iLabel.setAttribute("for", resourceRepeated + uiDetailsRepeated.key)
    iLabel.appendChild(iInput)
    iDiv.appendChild(iLabel)
    elRepeated.appendChild(iDiv)


}

function handleTimeElement(uiDetailsTime, resourceTime, elTime) {
    var iDiv = document.createElement('div');
    iDiv.setAttribute("class", "floating-label")
    iDiv.setAttribute("style", "margin:20px 0px 10px 0px;");
    var iInput = document.createElement('input');
    if (uiDetailsTime.hasOwnProperty("readonly") && uiDetailsTime.readonly == 'True') {
        iInput.disabled = true;
    }

    iInput.setAttribute("isconfig", "no")

    iInput.setAttribute("type", "timetext")
    iInput.setAttribute("class", "floating-input-protofields time-field")
    iInput.setAttribute("placeholder", "hh:mm:ss")

    if (localStorage.getItem('th') == 'light') {
        iInput.classList.add("input-light")
    }

    iInput.addEventListener('keyup', function (e) {
        let temp = e.target.value

        if ((e.keyCode > 47 && e.keyCode < 58) && e.keyCode !== 8 && (temp.length == 2 || temp.length == 5)) {
            temp = temp + ":"
            iInput.value = temp
        } else if (e.keyCode < 47 || e.keyCode > 58 || temp.length > 8) {
            temp = temp.substr(0, temp.length - 1)
            iInput.value = temp
        }
        if (temp.split(":")[0] > 23) {
            temp = ""
            iInput.value = ""
        } else if (temp.split(":")[1] > 59) {
            temp = temp.substr(0, temp.length - 3)
            iInput.value = temp
        } else if (temp.split(':')[2] > 59) {
            temp = temp.substr(0, temp.length - 2)
            iInput.value = temp
        }
    })

    iInput.setAttribute("id", resourceTime + uiDetailsTime.property)

    var iLabel = document.createElement('label');
    if (uiDetailsTime.hasOwnProperty('rpcproperty'))
        iLabel.setAttribute("rpcproperty", uiDetailsTime.rpcproperty)

    if (uiDetailsTime.hasOwnProperty('propertyText')) {
        iLabel.setAttribute("property", uiDetailsTime.property)
        iLabel.innerText = uiDetailsTime.propertyText
    } else {
        iLabel.innerText = uiDetailsTime.property
    }
    iLabel.setAttribute("style", "margin-top: -12px;left: 15px;background: #151617;font-size: 14px;")
    iLabel.setAttribute("class", "input-label")
    if (localStorage.getItem('th') === 'light') {
        iLabel.classList.add('label-light')
    } else if (localStorage.getItem('th') === 'dark') {
        iLabel.classList.remove('label-light')
    }
    iLabel.setAttribute("for", resourceTime + uiDetailsTime.property)

    iDiv.appendChild(iLabel)
    iDiv.appendChild(iInput)
    elTime.appendChild(iDiv)
}


function handleDropdownElement(uiDetailsDropdown, resourceDropdown, elDropdown) {
    var iDiv = document.createElement('div');
    iDiv.setAttribute("style", "margin:20px 0px 10px 0px;");
    iDiv.setAttribute("class", "floating-label")
    var select = document.createElement('select');
    select.setAttribute("class", "floating-protofields")

    if (uiDetailsDropdown.hasOwnProperty("readonly") && uiDetailsDropdown.readonly == 'True') {
        select.classList.add('disabled-selectField')
        select.disabled = true;
    }
    if (localStorage.getItem('th') === 'light') {
        select.classList.add('input-light')
    } else if (localStorage.getItem('th') === 'dark') {
        select.classList.remove('input-light')
    }
    select.setAttribute("style", "font-size: 12px;")
    select.setAttribute("id", resourceDropdown + uiDetailsDropdown.property)
    for (var modei in uiDetailsDropdown.mode) {
        var option = document.createElement('option');
        option.setAttribute("value", uiDetailsDropdown.mode[modei].value)
        option.innerText = uiDetailsDropdown.mode[modei].label
        select.appendChild(option)
    }
    var iLabel = document.createElement('label');
    if (uiDetailsDropdown.hasOwnProperty('rpcproperty'))
        iLabel.setAttribute("rpcproperty", uiDetailsDropdown.rpcproperty)

    if (uiDetailsDropdown.hasOwnProperty('propertyText')) {
        iLabel.setAttribute("property", uiDetailsDropdown.property)
        iLabel.innerText = uiDetailsDropdown.propertyText
    } else {
        iLabel.innerText = uiDetailsDropdown.property
    }

    iLabel.setAttribute("class", "input-label")
    if (localStorage.getItem('th') === 'light') {
        iLabel.classList.add('label-light')
    } else if (localStorage.getItem('th') === 'dark') {
        iLabel.classList.remove('label-light')
    }
    iLabel.setAttribute("style", "background:#151617;margin-top:-10px;left:15px; z-index:99;")
    iLabel.setAttribute("for", resourceDropdown + uiDetailsDropdown.property)

    iDiv.appendChild(iLabel)
    iDiv.appendChild(select)
    elDropdown.appendChild(iDiv)
}



function handleBoolElement(uiDetailsBool, resourceBool, elBool) {

    var iDiv = document.createElement('div');
    iDiv.setAttribute("style", "margin-bottom: 5px;");

    var iLabel = document.createElement('label');
    iLabel.setAttribute('class', "containercheck")

    if (localStorage.getItem('th') === 'light') {
        iLabel.classList.add('containercheck-light')
    } else if (localStorage.getItem('th') === 'dark') {
        iLabel.classList.remove('containercheck-light')
    }

    if (uiDetailsBool.hasOwnProperty('rpcproperty'))
        iLabel.setAttribute("rpcproperty", uiDetailsBool.rpcproperty)

    if (uiDetailsBool.hasOwnProperty('propertyText')) {
        iLabel.setAttribute("property", uiDetailsBool.property)
        iLabel.innerText = uiDetailsBool.propertyText
    } else {
        iLabel.innerText = uiDetailsBool.property
    }
    iLabel.setAttribute("for", resourceBool + uiDetailsBool.property)

    var iInput = document.createElement('input');
    if (uiDetailsBool.hasOwnProperty("readonly") && uiDetailsBool.readonly == 'True') {
        iInput.disabled = true;
    }

    iInput.setAttribute("isconfig", "no")
    iInput.setAttribute("type", "checkbox")
    iInput.setAttribute("data-toggle", "toggle")
    iInput.setAttribute("id", resourceBool + uiDetailsBool.property)
    spantag = document.createElement('span');
    spantag.setAttribute("class", "checkmark")
    if (localStorage.getItem('th') === 'light') {
        spantag.classList.add('checkTick-light')
    } else if (localStorage.getItem('th') === 'dark') {
        spantag.classList.remove('checkTick-light')
    }
    iDiv.appendChild(iLabel)

    iLabel.appendChild(iInput)
    iLabel.appendChild(spantag)
    elBool.appendChild(iDiv)
}


function handleIntFloatElement(uiDetailsIntFloat, resourceIntFloat, elIntFloat) {
    var iDiv = document.createElement('div');
    iDiv.setAttribute("class", "floating-label")
    iDiv.setAttribute("style", "margin:20px 0px 10px 0px;");
    iLabel = document.createElement('label');

    if (uiDetailsIntFloat.hasOwnProperty('rpcproperty'))
        iLabel.setAttribute("rpcproperty", uiDetailsIntFloat.rpcproperty)
    if (uiDetailsIntFloat.hasOwnProperty('propertyText')) {
        iLabel.setAttribute("property", uiDetailsIntFloat.property)
        iLabel.innerText = uiDetailsIntFloat.propertyText
    } else {
        iLabel.innerText = uiDetailsIntFloat.property
    }
    iLabel.setAttribute("class", "input-label")
    if (localStorage.getItem('th') === 'light') {
        iLabel.classList.add('input-light')
    } else if (localStorage.getItem('th') === 'dark') {
        iLabel.classList.remove('input-light')
    }
    iLabel.setAttribute("for", resourceIntFloat + uiDetailsIntFloat.property)
    iLabel.setAttribute("style", "background:#151617;margin-top:-12px;left:15px")

    iDiv.appendChild(iLabel)
    var iInput = document.createElement('input');
    if (uiDetailsIntFloat.hasOwnProperty("readonly") && uiDetailsIntFloat.readonly == 'True') {
        iInput.disabled = true;
    }
    iInput.setAttribute("isconfig", "no")
    iInput.setAttribute("type", "number")
    iInput.setAttribute("class", "floating-input-protofields")
    if (localStorage.getItem('th') === 'light') {
        iInput.classList.add('nInput-light')
    } else if (localStorage.getItem('th') === 'dark') {
        iInput.classList.remove('nInput-light')
    }
    iInput.setAttribute("style", "font-size: 16px;")

    iInput.setAttribute("min", uiDetailsIntFloat.minrange)
    iInput.setAttribute("value", (uiDetailsIntFloat.minrange).toString())
    iInput.setAttribute("max", uiDetailsIntFloat.maxrange)
    iInput.setAttribute("id", resourceIntFloat + uiDetailsIntFloat.property)
    iInput.setAttribute("name", resourceIntFloat + uiDetailsIntFloat.property)

    if (uiDetailsIntFloat.type == 'float') {
        if (uiDetailsIntFloat.minrange < 0) {
            iInput.setAttribute("onkeypress", "return (event.charCode >= 48 && event.charCode <= 57)|| event.charCode==46 || event.charCode==45")
        } else {
            iInput.setAttribute("onkeypress", "return (event.charCode >= 48 && event.charCode <= 57)|| event.charCode==46")
        }
    } else {
        if (uiDetailsIntFloat.minrange < 0) {
            iInput.setAttribute("onkeypress", "return (event.charCode >= 48 && event.charCode <= 57)|| event.charCode==45")
        } else {
            iInput.setAttribute("onkeypress", "return event.charCode >= 48 && event.charCode <= 57")
        }
    }
    iInput.setAttribute("oninput", "setRangeValues(this)")
    iInput.setAttribute("onblur", "onRangeBlur(this)")

    elIntFloat.appendChild(iDiv)
    iDiv.appendChild(iInput)

}

function handleStringElement(uiDetailsString, resourceString, elString) {

    var iDiv = document.createElement('div');
    //    iDiv.setAttribute('class', 'form-group')
    iDiv.setAttribute("class", "floating-label")
    iDiv.setAttribute("style", "margin:20px 0px 10px 0px;");
    var iInput = document.createElement('input');
    if (uiDetailsString.hasOwnProperty("readonly") && uiDetailsString.readonly == 'True') {
        iInput.disabled = true;
    }
    iInput.setAttribute("isconfig", "no")
    iInput.setAttribute("type", "text")
    iInput.setAttribute("class", "floating-input-protofields")
    //    iInput.setAttribute("placeholder", uiDetailsString.property)
    if (uiDetailsString.style == "large") {
        //        iInput.setAttribute("style", "float:right;width:55%;height:200px")

    } else if (uiDetailsString.style == "medium") {
        //        iInput.setAttribute("style", "float:right;width:55%;margin-bottom:100px")

    } else {
        //        iInput.setAttribute("style", "float:right;width:35%")
    }
    //    iInput.setAttribute("class", "form-control")
    iInput.setAttribute("id", resourceString + uiDetailsString.property)
    var iLabel = document.createElement('label');
    if (uiDetailsString.hasOwnProperty('rpcproperty'))
        iLabel.setAttribute("rpcproperty", uiDetailsString.rpcproperty)


    if (uiDetailsString.hasOwnProperty('propertyText')) {
        iLabel.setAttribute("property", uiDetailsString.property)
        iLabel.innerText = uiDetailsString.propertyText
    } else {
        iLabel.innerText = uiDetailsString.property
    }
    iLabel.setAttribute("style", "font-size: 15px;margin-top: -12px;left: 15px;background: #151617;")
    iLabel.setAttribute("class", "input-label")
    if (localStorage.getItem('th') === 'light') {
        iLabel.classList.add('label-light')
    } else if (localStorage.getItem('th') === 'dark') {
        iLabel.classList.remove('label-light')
    }
    iLabel.setAttribute("for", resourceString + uiDetailsString.property)
    iDiv.appendChild(iLabel)
    iDiv.appendChild(iInput)

    elString.appendChild(iDiv)


}


function design_layout(data, resource, servicename) {

    mask = []
    json_repeated_dict = {}
    var el = document.getElementById('uidesign');
    removeAllChildNodes(el)
    length = data['Configuration'].length
    for (i in data['Configuration']) {
        var iDiv = document.createElement('div');
        iDiv.setAttribute("class", "flex");
        var width = window.innerWidth;
        if (length <= 1) {
            iDiv.setAttribute("style", "width: " + 100 / length + "%; margin-bottom: 15px;");
        }
        else if (i == length - 1)
            iDiv.setAttribute("style", "margin-bottom: 15px");
        var iInput = document.createElement('input');
        iInput.setAttribute("isconfig", "yes")
        iInput.setAttribute("topic", data['Configuration'][i].topic)
        if (data['Configuration'][i].hasOwnProperty('rpcmethod'))
            iInput.setAttribute("rpc", data['Configuration'][i].rpcmethod)
        iInput.setAttribute("serviceclass", servicename)
        iInput.setAttribute("class", "flex");
        if (localStorage.getItem('th') === 'light') {
            iInput.classList.add('input-light')
        } else if (localStorage.getItem('th') === 'dark') {
            iInput.classList.remove('input-light')
        }
        if (data['Configuration'][i].hasOwnProperty('resource_name')) {
            iInput.setAttribute("resource_name", data['Configuration'][i].resource_name);

        }
        if (data['Configuration'][i].hasOwnProperty('name_key')) {
            iInput.setAttribute("name_key", data['Configuration'][i].name_key);

        }
        iInput.setAttribute("id", data['Configuration'][i].name);


        iInput.setAttribute("name", "flex");
        iInput.setAttribute("type", "radio");

        var iLabel = document.createElement('label');
        iLabel.setAttribute("class", "flex");
        if (localStorage.getItem('th') === 'light') {
            iLabel.classList.add('label-light')
        } else if (localStorage.getItem('th') === 'dark') {
            iLabel.classList.remove('label-light')
        }
        iLabel.setAttribute("style", "font-size: 16px;margin:2px 0px 0px 5px")
        iLabel.setAttribute("for", data['Configuration'][i].name)
        if (data['Configuration'][i].hasOwnProperty('display_name')) {
            iLabel.innerText = data['Configuration'][i].display_name
        } else {
            iLabel.innerText = data['Configuration'][i].name

        }
        iDiv.appendChild(iInput);
        iDiv.appendChild(iLabel);
        el.appendChild(iDiv)
        var rbConfig = document.getElementById(data['Configuration'][i].name)
        if (i == 0) {
            rbConfig.checked = true
            onConfigClick(rbConfig)
        }
        rbConfig.addEventListener('change', function () {
            // handle change
            onConfigClick(this)
        });
    }
    for (i in data['uidetails']) {
        if (data['uidetails'][i].type == 'label') {
            handleLabelElement(data['uidetails'][i], el);

        } else if (data['uidetails'][i].type == 'string') {
            handleStringElement(data['uidetails'][i], resource, el);
        }
        else if (data['uidetails'][i].type == 'int' || data['uidetails'][i].type == 'float') {
            handleIntFloatElement(data['uidetails'][i], resource, el);
        }
        else if (data['uidetails'][i].type == 'bool') {
            handleBoolElement(data['uidetails'][i], resource, el);

        }
        else if (data['uidetails'][i].type == 'dropdown') {
            handleDropdownElement(data['uidetails'][i], resource, el);

        }
        else if (data['uidetails'][i].type == 'time') {
            handleTimeElement(data['uidetails'][i], resource, el);

        } else if (data['uidetails'][i].type == 'repeated') {
            handleRepeatedlement(data['uidetails'][i], resource, el);
        }
    }


}
function closebtnClicked() {
    var modallg = document.getElementById("modal-lgss")
    var bottomcontent = document.getElementById("bottomcontent")
    var logbox = document.getElementById("logbox")
    //    var logboxdata = document.getElementById("logboxdata")
    bottomcontent.style.display = "none"
    modallg.style.display = "none"
    logbox.style.display = "none"
    //    logboxdata.style.display = "none"
    var sevice_status = document.getElementById('box-content');
    sevice_status.style.display = "block";
    serviceName = document.getElementById('back_pub').getAttribute("servicename")
    document.getElementById("cb" + serviceName).checked = false
}

function design_layout_repeated(data, key, repeated_class) {
    console.log("=====", data, key, repeated_class)
    document.getElementById("second_modal").innerText = key
    document.getElementById("second_modal").setAttribute("repeated_class", repeated_class)

    var repeatedbox = document.getElementById('repeatedbox');
    removeAllChildNodes(repeatedbox)
    for (var x in data) {

        if (data[x].type == 'label') {
            handleLabelElement(data[x], repeatedbox);

        }
        else if (data[x].type == 'string') {
            itDiv = handleStringElement(data[x], key, repeatedbox);
        }
        else if (data[x].type == 'int' || data[x].type == 'float') {
            itDiv = handleIntFloatElement(data[x], key, repeatedbox);
        }
        else if (data[x].type == 'bool') {
            itDiv = handleBoolElement(data[x], key, repeatedbox);
        }
        else if (data[x].type == 'dropdown') {
            itDiv = handleDropdownElement(data[x], key, repeatedbox);
        }
        else if (data[x].type == 'time') {
            itDiv = handleTimeElement(data[x], key, repeatedbox);
        }

    }

}
json_repeated_dict = {}


function add_repeated() {
    console.log("++++", add_repeated)
    json_repeated = {}
    inputs = document.getElementById('repeatedbox').getElementsByTagName('input');
    getAllUiValues(inputs, json_repeated)
    selects = document.getElementById('repeatedbox').getElementsByTagName('select');
    getAllDropDownValues(selects, json_repeated)
    $('#myModal2').modal('hide');
    value = json_repeated_dict[document.getElementById('second_modal').innerText]


    if (Object.keys(json_repeated).length == 1) {
        json_repeated = Object.values(json_repeated)[0]
    }
    if (typeof value == "undefined") {
        value = [json_repeated]
        json_repeated_dict[document.getElementById('second_modal').innerText] = value
    } else {
        json_repeated_dict[document.getElementById('second_modal').innerText].push(json_repeated)
    }

}
