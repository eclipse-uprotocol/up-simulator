function setPubSubDataOnPageLoad(data) {
  var pubdata = JSON.parse(data)
  removeAllChildNodes(document.getElementById("table_pub_sub"))
  for (i in pubdata) {
    setPubSubDataInUi(pubdata[i])
  }
  var arrCount = findCound(pubdata)
  document.getElementById('totalPublish').innerText = arrCount[0]
  document.getElementById('totalSubscribe').innerText = arrCount[1]
  document.getElementById('totalOnTopicUpdate').innerText = arrCount[2]
}
function findCound(data) {
  var arrCount = []
  let pubCount = 0
  let subCount = 0
  let updateCount = 0
  for (i in data) {
    if (data[i]['type'] == "Publish") {
      pubCount = pubCount + 1
    } else if (data[i]['type'] == 'Subscribe') {
      subCount = subCount + 1
    } else {
      updateCount = updateCount + 1
    }
  }
  arrCount[0] = pubCount
  arrCount[1] = subCount
  arrCount[2] = updateCount
  return arrCount
}
function setPubSubDataInUi(json_data) {

  tr = document.createElement("div")
  tr.setAttribute("style", "box-shadow: 0px 0px 3px 1px #5EB1F3;border-radius: 22.5021px;height:65px;width:100%;display:flex;margin-bottom:20px;")

  td = document.createElement("div")
  td.setAttribute("class", "col-xl-6")
  td.setAttribute("style", "border:none")
  h6 = document.createElement("h6")
  h6.setAttribute("class", "green-label")
  if (localStorage.getItem('th') === 'light') {
    h6.classList.add('greenlabel-light')
  }

  h6.innerText = json_data['topic'].split('/1/')[1]
  h6.setAttribute("style", "font-weight: 400;font-size: 16px;line-height: 26px;display: flex;align-items: center;text-align: center;color: #fff;width:100%;margin-top:15px")
  h6.style.color = "#6CC24A"
  td.appendChild(h6)
  tr.appendChild(td)

  td = document.createElement("div")
  td.setAttribute("class", "col-xl-4")
  h6 = document.createElement("h6")
  h6.innerText = json_data['type']
  h6.setAttribute("class", "para")
  if (localStorage.getItem('th') === 'light') {
    h6.classList.add('para-light')
  }
  h6.setAttribute("style", "font-weight: 400;font-size: 16px;line-height: 26px;display: flex;align-items: center;text-align: center;color: #fff;width:100%;margin-top:15px")
  td.appendChild(h6)
  tr.appendChild(td)

  td = document.createElement("div")
  seeMoreIcon = document.createElement("i")
  seeMoreIcon.setAttribute('class', "fa-solid fa-angles-right")
  td.setAttribute("class", "col-xl-2")
  td.setAttribute("style", "display: flex; align-items: center;")
  h6 = document.createElement("h6")
  h6.setAttribute("class", "seeMore")
  h6.appendChild(seeMoreIcon)
  h6.setAttribute("style", "text-decoration: underline;font-weight: 400;font-size: 16px;line-height: 26px;display: flex;align-items: center;text-align: center;color:  #39A0F1;;width:100%;border:none;background:none;justify-content:end;margin-left:-10px;")
  h6.addEventListener("click", function () {
    var boxcontent = document.getElementById("box-content")
    boxcontent.style.display = "none"
    var rpcselected = document.getElementById("topicSelected")
    topicSelected.style.display = "block"
    topicSelected.innerText = json_data['topic']

    document.getElementById("window_heading").style.display = "block"
    var dash_data = document.getElementById("dash_data")
    removeAllChildNodes(dash_data)
    if (json_data['type'] == 'OnTopicUpdate') {
      document.getElementById('window_heading').innerText = "Received Data"
    } else if (json_data['type'] == 'Publish') {
      document.getElementById('window_heading').innerText = "Published Data"
    } else {
      document.getElementById('window_heading').innerText = ''
    }


    div = document.createElement("div")
    h6 = document.createElement("h6")
    h6.setAttribute("class", "para")
    if (localStorage.getItem('th') === 'light') {
      h6.classList.add('para-light')
    }
    h6.setAttribute("style", "font-weight: 300;font-size: 16px;line-height: 150%;letter-spacing: -0.432733px;color:#FFFFFF")
    if (json_data['type'] != 'Subscribe') {
      h6.insertAdjacentHTML('beforeend', addColorToKeys(json_data['message']));
    }
    div.appendChild(h6)
    dash_data.appendChild(div)
    let cloudEventDiv = document.getElementById('pubsub-cloud-eventId')
    if (json_data.hasOwnProperty("ce_id") && json_data["ce_id"] != null) {
      cloudEventDiv.style.display = 'block'
      cloudEventDiv.innerText = "Cloud Event Id: " + json_data["ce_id"]
    } else {
      cloudEventDiv.style.display = 'none'
    }


  }, false)
  td.appendChild(h6)
  tr.appendChild(td)

  document.getElementById("table_pub_sub").prepend(tr)
}

function exportPubReport() {
  if (document.getElementById("table_pub_sub").childElementCount > 0)
    window.location.href = '/downloadPubSubReport';
}


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


