function myFunctionmock() {
    var input, filter, ul, li, a, i, txtValue;
    searchinput = document.getElementById("searchmock");
    filter = searchinput.value.toUpperCase();
    ul = document.getElementById("tableMockService");
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

function getMockServices() {
    fetch("/getmockservices")
        .then((res) => res.json())
        .then((data) => {
            if (data.result) {
                console.log(data);
                document.getElementById('apksdialog').setAttribute("style", "display:block")
                design_apk_list_layoutMock(data)
            } else {
                document.getElementById('apksdialog').setAttribute("style", "display:none")
            }

        })
}

function design_apk_list_layoutMock(data) {
    removeAllChildNodes(document.getElementById('tableMockService'))
    var service_status = document.getElementById('box-content');
    let running_services = data.running
    document.getElementById("startAll").setAttribute("tagpkg", JSON.stringify(data.pkgs_mock))
    for (let i in data.pkgs_mock) {
        document.getElementById('tableMockService').appendChild(createUIApksMock(data.pkgs_mock, i))
        for (let k in running_services) {

            if (running_services[k] == data.pkgs_mock[i].entity) {
                service_status.style.display = "none";
                design_service_status_layout(data.pkgs_mock[i].name, data.pkgs_mock[i].entity, "Loading")
                refreshMockServiceStatus(data.pkgs_mock[i].entity, true)
                document.getElementById("cb" + data.pkgs_mock[i].entity).checked = true
                break;
            }
        }



    }
}
const box_content_list = []
function createUIApksMock(pkgs, i) {
    let input = document.createElement('input')
    let litag = document.createElement('li')
    let divtag = document.createElement('div')
    let atag = document.createElement('a')
    atag.setAttribute("class", "atagclass")
    input.setAttribute("type", "checkbox")
    input.setAttribute("id", "cb" + pkgs[i].entity)
    input.setAttribute('key', pkgs[i].entity)
    input.addEventListener("click", function () {
        var sevice_status = document.getElementById('box-content');
        sevice_status.style.display = "none";
        if (document.getElementById("cb" + pkgs[i].entity).checked) {
            design_service_status_layout(pkgs[i].name, pkgs[i].entity, "Loading")
            let json = { "entity": pkgs[i].entity, "key": pkgs[i].key }
            console.log("json=", json)
            socket.emit('start-service', json);
        }
        else {
            console.log("uncheck")
            uncheck_id = document.getElementById(pkgs[i].entity);
            // Stopping mock serice
            stopMockService(pkgs[i].entity)
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

    //console.log(atag.appendChild(label))
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
    //console.log("Label", label)
    atag.appendChild(label)
    litag.appendChild(atag)


    return litag
}

function design_service_status_layout(name, entity, status) {
    box_content_list.push(entity)
    let div = document.createElement('div')
    div.setAttribute("class", "servicecontent")
    const button = document.createElement('div')

    button.setAttribute("class", "buttonload")
    if (localStorage.getItem('th') === 'light') {
        button.classList.add('buttonload-light')
    } else if (localStorage.getItem('th') === 'dark') {
        button.classList.remove('buttonload-light')
    }

    button.setAttribute("id", "buttonload" + entity)
    if (name.includes("Service")) {
        button.innerHTML = name;
    } else {
        button.innerHTML = name + " Service";
    }
    var icon = document.createElement('i');
    icon.className = "fa fa-refresh fa-spin statusIcon";
    if (localStorage.getItem('th') === 'light') {
        icon.classList.add('icon-light')
    } else if (localStorage.getItem('th') === 'dark') {
        icon.classList.remove('icon-light')
    }
    var iconId = entity + "Mock";
    icon.setAttribute("id", iconId)
    const divElement = document.createElement("div");
    const divicon = document.createElement("div");
    divicon.setAttribute("class", "icon-container");
    divicon.setAttribute("id", "icon" + entity);
    divicon.appendChild(icon);
    divicon.addEventListener('click', () => stopMockService(entity))
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
    document.querySelector(".servicedata").hidden = false
    document.querySelector(".servicedata").appendChild(button);
    document.querySelector(".servicedata").appendChild(divElement);
    document.querySelector(".servicedata").appendChild(divicon);
}

function stopMockService(id){
  uncheck_id = document.getElementById(id);
  uncheckIcon_id = document.getElementById("icon" + id);
  uncheckbutton_id = document.getElementById("buttonload" + id);
  document.querySelector(".servicedata").removeChild(uncheck_id);
  document.querySelector(".servicedata").removeChild(uncheckbutton_id);
  document.querySelector(".servicedata").removeChild(uncheckIcon_id);

  activeCheckbox = document.getElementById("cb"+id)
  activeCheckbox.checked = false

  fetch("/updateservicestatus?entity=" + id + "&file=service_status.txt")
  .then((res) => res.json())
  .then((data) => {
  if (data.result) {

  }
  }).catch((error) => console.log(error));
}

function startAllMockServices() {
    console.log("all mock service starting...")
    var pkgs = document.getElementById("startAll");
    if(pkgs){
        pkgs = JSON.parse(pkgs.getAttribute("tagpkg"))
        var sevice_status = document.getElementById('box-content');
        sevice_status.style.display = "none";
        for (i in pkgs) {
            if (document.getElementById("cb" + pkgs[i].entity).checked) {
                continue;
            } else {
                document.getElementById("cb" + pkgs[i].entity).checked = true
                design_service_status_layout(pkgs[i].name, pkgs[i].entity, "Loading")
                let json = { "entity": pkgs[i].entity, "key": pkgs[i].key }
                console.log("json=", json)
                socket.emit('start-service', json);
            }
        }
    } else {
        fetch("/getmockservices")
            .then((res) => res.json())
            .then((data) => {
                if (data.result) {
                    const pkgs = data.pkgs_mock
                    const already_running = data.running;
                    for (var i in pkgs) {
                        if (already_running.find((entity) => (entity == pkgs[i].entity))){
                            continue;
                        } else {
                            let json = { "entity": pkgs[i].entity, "key": pkgs[i].key }
                            //console.log("commonjs_json=", json)
                            socket.emit('start-service', json);
                        }
                    }
                }
            })



    }


}
function refreshMockServiceStatus(key, isAlreadyRunning) {
    // save service running status

    changeIconId = key + "Mock";
    changeStatus = document.getElementById(key);
    changeStatusIcon = document.getElementById(changeIconId)
    if(changeStatus){
        changeStatus.textContent = "Running";
        changeStatus.style.color = "green";
    }
    if(changeStatusIcon){
        changeStatusIcon.classList.remove("fa", "fa-refresh", "fa-spin", "statusIcon");
        changeStatusIcon.classList.add("fa", "fa", "fa-solid", "fa-stop", "stopIcon");
    }
}


function stopAllMockServices() {
    var pkgs = document.getElementById("startAll");
    if(pkgs){
        pkgs = JSON.parse(pkgs.getAttribute("tagpkg"));
    } else {
        pkgs = {};
    }
    var service_status = document.getElementById('box-content');
    var serviceData = document.getElementById("hiddenservicedata");
    if(serviceData){
        serviceData.hidden = true;
    }
    if(service_status){
        service_status.style.display = "block";
    }
    console.log(pkgs);
    for (i in pkgs) {
        var checkboxId = "cb" + pkgs[i].entity;
        console.log(checkboxId);
        var service_checkbox = document.getElementById(checkboxId);
        console.log(service_checkbox);
        if(service_checkbox){
            service_checkbox.checked = false;
            //console.log("@@@@@@@@@@@@@@@@@@@@@@@@@@@entityj@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@2")
        }
    }
    socket.emit('stop_all_mockservices');
}
