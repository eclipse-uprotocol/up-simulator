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
let toggler = document.querySelector('.toggle')

let toggleTheme = function (elem) {
    let sidebarFooter = document.querySelector('.sidebarFooter')
    let maincontentElement = document.querySelector('.maincontent')
    let configurationText = document.querySelector('.configuration')
    let boxContentData = document.querySelectorAll('.box-content-data')
    let tableElements = document.querySelectorAll('table')
    let headerElement = document.querySelectorAll('.headerfont')
    let anchorElements = document.querySelectorAll('a')
    let scrollNav = document.querySelector('.navbar-wrapper')
    let labelElements = document.querySelectorAll('label')
    let selectElements = document.querySelectorAll('select')
    let inputElements = document.querySelectorAll('input')
    let buttonElements = document.querySelectorAll('button')

    let cardServicesElements = document.querySelectorAll('.card')
    let subText = document.querySelectorAll('.mb-0')
    let buttonLoadElements = document.querySelectorAll('.buttonload')
    let paraElements = document.querySelectorAll('.para')
    let checkElements = document.querySelectorAll('.containercheck')
    let textStart = document.querySelector('.text-start')
    let boxContent = document.querySelector('#box-content')
    let flexElements = document.querySelectorAll('.flex')
    let h4Elements = document.querySelectorAll('h4')
    let numberInputElements = document.querySelectorAll('.floating-input-protofields')
    let inputLabel = document.querySelectorAll('.input-label')
    let logBox = document.querySelector('#logbox')
    let floatingProtoField = document.querySelectorAll('.floating-protofields')
    let h6Elements = document.querySelectorAll('.subHeading')
    let svgElements = document.querySelectorAll('.statusIcon')
    let dashboardTitles = document.querySelectorAll('.dashboardTitle')
    let checkTickElement = document.querySelectorAll('.checkmark')
    let subMenuElements = document.querySelectorAll('.pcoded-submenu')
    let modalElement = document.querySelector('#modal-mask')
    let mockServicesElement = document.querySelector('#mockServicesCard')
    let radioButtonElements = document.querySelectorAll('.customRadio')
    let startMocks = document.querySelectorAll('.startMock')
    let sidebarHeadingElements = document.querySelectorAll('.sidebarHeading')
    let activeElement = document.querySelector('.active')
    let logoImgElement = document.querySelector('#logoImg')
    let navbarElement = document.querySelector('.navbar-brand')
    let buttonContent = document.querySelectorAll('.btn-content')
    let btndelete = document.querySelector('.btn-delete')
    let uiModalBox = document.querySelectorAll('.customModal')
    let greenLabel = document.querySelectorAll('.green-label')
    let lightLogo = document.getElementById('logo-light')
    let successTextElements = document.querySelectorAll('.logs-success')

    let navbarStrap = document.querySelector('.R-navbar-strap')
    let navbarToggler = document.querySelector('.navbar-toggler')
    let navbarCloser = document.querySelector('.navbar-closer')

    console.log('light logooo', navbarToggler)

    if (localStorage.getItem('th') === 'light') {

        if (successTextElements) {
            for (let i = 0; i < successTextElements.length; i++) {
                successTextElements[i].classList.add('logs-success-light')
            }
        }

        activeElement && activeElement.classList.add('active-light')
        lightLogo.style.display = "block"
        if (startMocks) {
            for (let i = 0; i < startMocks.length; i++) {
                startMocks[i].classList.add('box-content-data-light')
            }
        }
        for (let i = 0; i < subMenuElements.length; i++) {
            subMenuElements[i].id = 'submenu-light'
        }

    } else if (localStorage.getItem('th') === 'dark') {
        if (successTextElements) {
            for (let i = 0; i < successTextElements.length; i++) {
                successTextElements[i].classList.remove('logs-success-light')
            }
        }
        lightLogo.style.display = "none"
        activeElement && activeElement.classList.remove('active-light')
        if (startMocks) {
            for (let i = 0; i < startMocks.length; i++) {
                startMocks[i].classList.remove('box-content-data-light')
            }
        }
        for (let i = 0; i < subMenuElements.length; i++) {
            subMenuElements[i].removeAttribute('id')
        }
    }

    if (elem.checked) {
        navbarToggler && navbarToggler.classList.add('navbarToggler-light')
        navbarCloser && navbarCloser.classList.add('navbarCloser-light')
        navbarStrap && navbarStrap.classList.add('R-navbar-strap-light')

        if (successTextElements) {
            for (let i = 0; i < successTextElements.length; i++) {
                successTextElements[i].classList.add('logs-success-light')
            }
        }
        lightLogo.style.display = "block"
        logoImgElement.src = '/static/icons/lightThemeLogo-fotor-bg-remove.png'
        logoImgElement.style.height = '50px'
        logoImgElement.style.width = '150px'
        logoImgElement.style.display = 'none';

        navbarElement.classList.add('navbarBrand-light')

        if (btndelete) {
            btndelete.classList.add('btn-delete-light')
        }
        if (greenLabel) {
            for (let i = 0; i < greenLabel.length; i++) {
                greenLabel[i].classList.add('greenlabel-light')
            }
        }
        if (uiModalBox) {
            for (let i = 0; i < uiModalBox.length; i++) {
                uiModalBox[i].classList.add('modal-light')
            }
        }
        if (buttonContent) {
            for (let i = 0; i < buttonContent.length; i++) {
                buttonContent[i].classList.remove('button-light')
                buttonContent[i].classList.add('buttonContent-light')
            }
        }

        for (let i = 0; i < sidebarHeadingElements.length; i++) {
            sidebarHeadingElements[i].classList.add('sidebarText-light')
        }

        if (startMocks) {
            for (let i = 0; i < startMocks.length; i++) {
                startMocks[i].classList.add('box-content-data-light')
            }
        }
        mockServicesElement && mockServicesElement.classList.add('noBorder')
        modalElement && modalElement.classList.add('modal-light')

        if (radioButtonElements) {
            for (let i = 0; i < radioButtonElements.length; i++) {
                radioButtonElements[i].classList.add('radio-light')
            }
        }

        for (let i = 0; i < subMenuElements.length; i++) {
            subMenuElements[i].id = 'submenu-light'
        }
        if (activeElement) {
            activeElement.classList.add('active-light')
        }
        localStorage.setItem('th', 'light')
        for (let i = 0; i < boxContentData.length; i++) {
            boxContentData[i].classList.add('box-content-data-light')
        }
        for (let i = 0; i < tableElements.length; i++) {
            tableElements[i].classList.add('table-light')
        }
        for (let i = 0; i < headerElement.length; i++) {
            headerElement[i].classList.add('headerElement-light')
        }
        for (let i = 0; i < anchorElements.length; i++) {
            anchorElements[i].classList.add('anchor-light')
        }
        for (let i = 0; i < labelElements.length; i++) {
            labelElements[i].classList.add('label-light')
        }
        for (let i = 0; i < selectElements.length; i++) {
            selectElements[i].classList.add('select-light')
        }
        for (let i = 0; i < inputElements.length; i++) {
            inputElements[i].classList.add('input-light')
        }
        for (let i = 0; i < buttonElements.length; i++) {
            buttonElements[i].classList.add('button-light')
        }
        for (let i = 0; i < cardServicesElements.length; i++) {
            cardServicesElements[i].classList.add('card-light')
        }
        if (subText) {
            for (let i = 0; i < subText.length; i++) {
                subText[i].classList.add('subText-light')
            }
        }

        if (buttonLoadElements) {
            for (let i = 0; i < buttonLoadElements.length; i++) {
                buttonLoadElements[i].classList.add('buttonload-light')
            }
        }

        if (paraElements) {
            for (let i = 0; i < paraElements.length; i++) {
                paraElements[i].classList.add('para-light')
            }
        }
        if (checkElements) {
            for (let i = 0; i < checkElements.length; i++) {
                checkElements[i].classList.add('containercheck-light')
            }
        }
        if (textStart) {
            textStart.classList.add('textStart-light')
        }
        if (boxContent) {
            boxContent.classList.add('boxContent-light')
        }
        for (i = 0; i < h4Elements.length; i++) {
            h4Elements[i].classList.add('h4-light')
        }
        for (i = 0; i < numberInputElements.length; i++) {
            numberInputElements[i].classList.add('nInput-light')
        }
        for (i = 0; i < inputLabel.length; i++) {
            inputLabel[i].classList.add('input-light')
        }

        if (floatingProtoField) {
            for (let i = 0; i < floatingProtoField.length; i++) {
                floatingProtoField[i].classList.add('input-light')
            }
        }
        if (h6Elements) {
            for (let i = 0; i < h6Elements.length; i++) {
                h6Elements[i].classList.add('subHeading-light')
            }
        }
        if (svgElements) {
            for (let i = 0; i < svgElements.length; i++) {
                svgElements[i].classList.add('icon-light')
            }
        }
        if (dashboardTitles) {
            for (let i = 0; i < dashboardTitles.length; i++) {
                dashboardTitles[i].classList.add('dashboardTitles-light')
            }
        }
        if (checkTickElement) {
            for (let i = 0; i < checkTickElement.length; i++) {
                checkTickElement[i].classList.add('checkTick-light')
            }
        }



        sidebarFooter.classList.add('sidebarFooter-light')
        maincontentElement.classList.add('maincontent-light')
        configurationText.id = 'text-light'
        scrollNav.classList.add('nav-light')
        logBox && logBox.classList.add('logBox-light')
        console.log('light mode')

    } else {
        navbarToggler && navbarToggler.classList.remove('navbarToggler-light')
        navbarCloser && navbarCloser.classList.remove('navbarCloser-light')
        navbarStrap && navbarStrap.classList.remove('R-navbar-strap-light')


        if (successTextElements) {
            for (let i = 0; i < successTextElements.length; i++) {
                successTextElements[i].classList.remove('logs-success-light')
            }
        }
        if (btndelete) {
            btndelete.classList.remove('btn-delete-light')
        }
        if (greenLabel) {
            for (let i = 0; i < greenLabel.length; i++) {
                greenLabel[i].classList.remove('greenlabel-light')
            }
        }
        if (uiModalBox) {
            for (let i = 0; i < uiModalBox.length; i++) {
                uiModalBox[i].classList.remove('modal-light')
            }
        }
        logoImgElement.style.display = 'block';
        lightLogo.style.display = "none"

        navbarElement.classList.remove('navbarBrand-light')
        logoImgElement.src = '/static/icons/sim_logo.svg'
        logoImgElement.style.height = '80px'
        logoImgElement.style.width = '200px'

        if (buttonContent) {
            for (let i = 0; i < buttonContent.length; i++) {
                buttonContent[i].classList.remove('button-light')
                buttonContent[i].classList.remove('buttonContent-light')
            }
        }

        for (let i = 0; i < sidebarHeadingElements.length; i++) {
            sidebarHeadingElements[i].classList.remove('sidebarText-light')
        }
        if (startMocks) {
            for (let i = 0; i < startMocks.length; i++) {
                startMocks[i].classList.remove('box-content-data-light')
            }
        }

        if (modalElement) {
            modalElement.classList.remove('modal-light')
        }
        mockServicesElement && mockServicesElement.classList.remove('noBorder')

        for (let i = 0; i < subMenuElements.length; i++) {
            subMenuElements[i].removeAttribute('id')
        }

        if (activeElement) {
            activeElement && activeElement.classList.remove('active-light')
        }
        localStorage.setItem('th', 'dark')

        for (let i = 0; i < boxContentData.length; i++) {
            boxContentData[i].classList.remove('box-content-data-light')
        }
        for (let i = 0; i < tableElements.length; i++) {
            tableElements[i].classList.remove('table-light')
        }
        for (let i = 0; i < headerElement.length; i++) {
            headerElement[i].classList.remove('headerElement-light')
        }

        for (let i = 0; i < anchorElements.length; i++) {
            anchorElements[i].classList.remove('anchor-light')
        }
        for (let i = 0; i < labelElements.length; i++) {
            labelElements[i].classList.remove('label-light')
        }
        for (let i = 0; i < selectElements.length; i++) {
            selectElements[i].classList.remove('select-light')
        }
        for (let i = 0; i < inputElements.length; i++) {
            inputElements[i].classList.remove('input-light')
        }
        for (let i = 0; i < buttonElements.length; i++) {
            buttonElements[i].classList.remove('button-light')
        }

        for (let i = 0; i < cardServicesElements.length; i++) {
            cardServicesElements[i].classList.remove('card-light')
        }
        if (subText) {
            for (let i = 0; i < subText.length; i++) {
                subText[i].classList.remove('subText-light')
            }
        }
        if (buttonLoadElements) {
            for (let i = 0; i < buttonLoadElements.length; i++) {
                buttonLoadElements[i].classList.remove('buttonload-light')
            }
        }

        if (paraElements) {
            for (let i = 0; i < paraElements.length; i++) {
                paraElements[i].classList.remove('para-light')
            }
        }


        if (checkElements) {
            for (let i = 0; i < checkElements.length; i++) {
                checkElements[i].classList.remove('containercheck-light')
            }
        }
        if (textStart) {
            textStart.classList.remove('textStart-light')
        }
        if (boxContent) {
            boxContent.classList.remove('boxContent-light')
        }
        for (i = 0; i < h4Elements.length; i++) {
            h4Elements[i].classList.remove('h4-light')
        }
        for (i = 0; i < numberInputElements.length; i++) {
            numberInputElements[i].classList.remove('nInput-light')
        }
        for (i = 0; i < inputLabel.length; i++) {
            inputLabel[i].classList.remove('input-light')
        }

        if (floatingProtoField) {
            for (let i = 0; i < floatingProtoField.length; i++) {
                floatingProtoField[i].classList.remove('input-light')
            }
        }

        if (h6Elements) {
            for (let i = 0; i < h6Elements.length; i++) {
                h6Elements[i].classList.remove('subHeading-light')
            }
        }

        if (svgElements) {
            for (let i = 0; i < svgElements.length; i++) {
                svgElements[i].classList.remove('icon-light')
            }
        }

        if (dashboardTitles) {
            for (let i = 0; i < dashboardTitles.length; i++) {
                dashboardTitles[i].classList.remove('dashboardTitles-light')
            }
        }
        if (checkTickElement) {
            for (let i = 0; i < checkTickElement.length; i++) {
                checkTickElement[i].classList.remove('checkTick-light')
            }
        }


        maincontentElement.classList.remove('maincontent-light')
        configurationText.removeAttribute('id')
        sidebarFooter.classList.remove('sidebarFooter-light')
        scrollNav.classList.remove('nav-light')
        logBox && logBox.classList.remove('logBox-light')


        console.log('DARK MODE')
    }
}


if (localStorage.getItem('th') === 'light') {
    toggler.checked = true
    toggleTheme(toggler)
} else if (localStorage.getItem('th') === 'dark') {
    toggler.checked = false
    toggleTheme(toggler)
}

