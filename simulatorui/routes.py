# -------------------------------------------------------------------------
#
# Copyright (c) 2023 General Motors GTO LLC
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
# SPDX-FileType: SOURCE
# SPDX-FileCopyrightText: 2023 General Motors GTO LLC
# SPDX-License-Identifier: Apache-2.0
#
# -------------------------------------------------------------------------

import os

from flask import redirect, url_for, render_template, request

from simulatorui import blueprint
from simulatorui.utils import adb_commands


@blueprint.route('/')
def route_default():
    return redirect(url_for('simulator_blueprint.route_setup'))


@blueprint.route('/configuration.html')
def route_setup():
    global sdk_version, portal_version
    deviceInfo = {'Image': "", 'Build_date': "", 'Build_id': "", 'Model': ""}
    emu_status='Emulator is not running'
    try:
        device = adb_commands.get_emulator_device()
        if device is not None:
            status = device.shell("getprop init.svc.bootanim")
            if status.__contains__('stopped'):
                emu_status = 'Emulator is running'
                os.system("adb forward tcp:6095 tcp:6095")
                deviceInfo = {'Image': device.shell("getprop ro.product.bootimage.name"),
                              'Build_date': device.shell("getprop ro.bootimage.build.date"),
                              'Build_id': device.shell("getprop ro.bootimage.build.id"),
                              'Model': device.shell("getprop ro.product.model")}
            else:
                emu_status = 'Emulator is loading'


    except Exception:
        pass

    return render_template('home/configuration.html', segment=get_segment(request), deviceInfo=deviceInfo,
                           emu_status=emu_status)


# Helper - Extract current page name from request
def get_segment(request):
    try:
        segment = request.path.split('/')[-1]
        if segment == '':
            segment = 'index'

        return segment

    except:
        return None
