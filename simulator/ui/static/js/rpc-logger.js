/*
SPDX-FileCopyrightText: 2024 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

This program and the accompanying materials are made available under the
terms of the Apache License Version 2.0 which is available at

    http://www.apache.org/licenses/LICENSE-2.0

SPDX-License-Identifier: Apache-2.0
*/

function setDataOnPageLoad(data) {
  var rpcdata = JSON.parse(data)
  removeAllChildNodes(document.getElementById("table_rpc"))
  for (i in rpcdata) {
    setDataInUi(rpcdata[i])
  }
}

function setDataInUi(json_data) {

  tr = document.createElement("div")
  tr.setAttribute("style", "box-shadow: 0px 0px 3px 1px #5EB1F3;border-radius: 22.5021px;height:65px;width:100%;display:flex;margin-bottom:20px;")

  td = document.createElement("div")
  td.setAttribute("class", "col-xl-6")
  td.setAttribute("style", "border:none; overflow: auto;")

  h6 = document.createElement("h6")
  h6.setAttribute("class", "green-label")
  if (localStorage.getItem('th') === 'light') {
    h6.classList.add("greenlabel-light")
  }

  h6.innerText = json_data['methodname']
  h6.setAttribute("style", "font-weight: 400;font-size: 16px;line-height: 26px;display: flex;align-items: center;text-align: center;color: #fff;width:100%;margin-top:15px")

  if (json_data["isfailed"]) {
    h6.style.color = "#E35205"
  } else {
    h6.style.color = "#6CC24A"
  }
  td.appendChild(h6)
  tr.appendChild(td)



  td = document.createElement("div")
  td.setAttribute("class", "col-xl-4")
  h6 = document.createElement("h6")
  h6.setAttribute("class", "para")
  if (localStorage.getItem('th') === 'light') {
    h6.classList.add("para-light")
  }
  h6.innerText = json_data['time']
  h6.setAttribute("style", "font-weight: 400;font-size: 16px;line-height: 18px;display: flex;align-items: center;text-align: center;color: #fff;width:100%;margin-top:1rem")
  td.appendChild(h6)
  tr.appendChild(td)

  td = document.createElement("div")
  seeMoreIcon = document.createElement("i")
  seeMoreIcon.setAttribute('class', "fa-solid fa-angles-right")
  td.setAttribute("class", "col-xl-2")
  td.setAttribute("style", "display:flex; justify-content: center;")
  h6 = document.createElement("h6")
  h6.setAttribute("class", "seeMore")
  h6.appendChild(seeMoreIcon)
  h6.setAttribute("style", "text-decoration: underline;font-weight: 400;font-size: 16px;line-height: 26px;display: flex;align-items: center;text-align: center;color:  #39A0F1;;width:100%;border:none;background:none;justify-content:flex-end")
  h6.addEventListener("click", function () {
    var boxcontent = document.getElementById("box-content")
    boxcontent.style.display = "none"
    var rpcselected = document.getElementById("rpcselected")
    rpcselected.setAttribute("class", "para")
    if (localStorage.getItem('th') === 'light') {
      rpcselected.classList.add('para-light')
    }
    rpcselected.style.display = "block"
    rpcselected.innerText = json_data['methodname']
    var resHeading = document.getElementById("responseHeading")
    resHeading.style.display = "block"
    resHeading.setAttribute("class", "para")
    if (localStorage.getItem('th') === 'light') {
      resHeading.classList.add('para-light')
    }
    var response = document.getElementById("response")
    removeAllChildNodes(response)

    var pubHeading = document.getElementById("publishedHeading")
    pubHeading.style.display = "block"
    pubHeading.setAttribute("class", "para")
    if (localStorage.getItem('th') === 'light') {
      pubHeading.classList.add('para-light')
    }
    var publisheddata = document.getElementById("publisheddata")
    removeAllChildNodes(publisheddata)

    var reqHeading = document.getElementById("requestHeading")
    reqHeading.setAttribute("class", "para")
    if (localStorage.getItem('th') === 'light') {
      reqHeading.classList.add('para-light')
    }
    reqHeading.style.display = "block"
    var request = document.getElementById("request")
    removeAllChildNodes(request)

    div = document.createElement("div")
    h6 = document.createElement("h6")
    h6.setAttribute("class", "para")
    if (localStorage.getItem('th') === 'light') {
      h6.classList.add('para-light')
    }
    h6.setAttribute("style", "font-weight: 300;font-size: 16px;line-height: 150%;letter-spacing: -0.432733px;color:#FFFFFF")
    h6.insertAdjacentHTML('beforeend', addColorToKeys(json_data['request']));
    div.appendChild(h6)
    request.appendChild(div)

    div = document.createElement("div")
    h6 = document.createElement("h6")
    h6.setAttribute("class", "para")
    if (localStorage.getItem('th') === 'light') {
      h6.classList.add('para-light')
    }

    h6.setAttribute("style", "font-weight: 300;font-size: 16px;line-height: 150%;letter-spacing: -0.432733px;color:#FFFFFF")

    h6.insertAdjacentHTML('beforeend', addColorToKeys(json_data['response']));

    div.appendChild(h6)
    response.appendChild(div)

    div = document.createElement("div")
    h6 = document.createElement("h6")
    h6.setAttribute("class", "para")
    if (localStorage.getItem('th') === 'light') {
      h6.classList.add('para-light')
    }
    h6.setAttribute("style", "font-weight: 300;font-size: 16px;line-height: 150%;letter-spacing: -0.432733px;color:#FFFFFF")

    h6.insertAdjacentHTML('beforeend', addColorToKeys(json_data['data']));
    div.appendChild(h6)
    publisheddata.appendChild(div)

    let cloudEventDiv = document.getElementById('rpc-dashboard-cloud-eventId')

    if (json_data.hasOwnProperty("ce_id") && json_data["ce_id"] != null) {
      cloudEventDiv.style.display = 'block'
      cloudEventDiv.innerText = "Cloud Event Id: " + json_data["ce_id"]
    } else {
      cloudEventDiv.style.display = 'none'
    }

  }, false)
  td.appendChild(h6)
  tr.appendChild(td)

  document.getElementById("table_rpc").prepend(tr)



  document.getElementById('totalRPC').innerText = json_data['rpccount']
  document.getElementById('successrpc').innerText = json_data['successrpc']
  document.getElementById('failedrpc').innerText = json_data['failedrpc']
  successper = (json_data['successrpc'] / json_data['rpccount']) * 100
  document.getElementById('successpercentage').innerText = successper.toFixed(2) + "%"
  failedper = (json_data['failedrpc'] / json_data['rpccount']) * 100
  document.getElementById('failedpercentage').innerText = failedper.toFixed(2) + "%"

}

function exportRPCReport() {
  if (document.getElementById("table_rpc").childElementCount > 0)
    window.location.href = '/downloadRPCReport';
}


// Function to add colors to JSON keys and format as pretty JSON
function addColorToKeys(obj, parentKey = '') {
  let jsonString = '{<br>';

  const keys = Object.keys(obj);

  for (let i = 0; i < keys.length; i++) {
    const key = keys[i];

    // Add indentation
    jsonString += ' '.repeat(parentKey.length + 2);

    // Create a <span> element for each key
    const spanElement = document.createElement("span");
    spanElement.textContent = `"${key}"`;
    spanElement.style.color = "#F0B323";
    jsonString += spanElement.outerHTML;

    jsonString += ': ';

    if (typeof obj[key] === "object" && obj[key] !== null) {
      // For nested objects, call the function recursively with the updated parent key
      jsonString += addColorToKeys(obj[key], `${parentKey}${key}.`);
    } else {
      // Wrap the value in quotes
      jsonString += `"${obj[key]}"`;
    }

    if (i !== keys.length - 1) {
      jsonString += ',';
    }

    jsonString += '<br>';
  }

  // Add closing brace and indentation
  jsonString += ' '.repeat(parentKey.length) + '}';

  return jsonString;
}
