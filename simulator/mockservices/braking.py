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

import re

from target.protofiles.common.health_state_pb2 import HealthState
from target.protofiles.vehicle.chassis.braking.v1.braking_service_pb2 import ResetHealthRequest, ManageHealthMonitoringRequest
from target.protofiles.vehicle.chassis.braking.v1.braking_topics_pb2 import BrakePads
from uprotocol.proto.umessage_pb2 import UMessage
from uprotocol.transport.ulistener import UListener

from simulator.core.abstract_service import BaseService
from simulator.core.exceptions import ValidationError
from simulator.utils.constant import KEY_URI_PREFIX


class BrakingService(BaseService):
    """
    The BrakingService object handles mock services for the lighting interior service
    """

    brake_names = []
    timeout = 9  # timeout time in seconds for discovery service
    state = {}

    def __init__(self, portal_callback=None):
        """
        BrakingService constructor
        """

        super().__init__("chassis.braking", portal_callback)
        self.init_state()

    def start_rpc_service(self):
        super().start_rpc_service()
        self.subscribe(
            [
                KEY_URI_PREFIX + "/chassis.braking/1/brake_pads.front#BrakePads",
                KEY_URI_PREFIX + "/chassis.braking/1/brake_pads.rear#BrakePads",
            ],
            BrakingPreconditions(self),
        )

    def init_state(self):
        """
        Initializes internal data structures for keeping track of the current state of the braking service
        """
        self.state = {}

        for brake in BrakePads.Resources.keys():
            brake = "brake_pads." + brake
            self.brake_names.append(brake)
            self.state[brake] = self.init_message_state(BrakePads)
            self.state[brake]["name"] = brake
            self.state[brake]["health"] = self.init_message_state(HealthState)

        self.state["brake_pads"] = self.init_message_state(ManageHealthMonitoringRequest)

    def set_topic_state(self, uri, message):
        """
        Sets state dictionary with values passed by the uBus, overwritting default values assigned during initialization

        Args:
            uri (str): String to identify specific car component eg.
            up:/chassis.suspension/1/ride_height_system_status#RideHeightSystemStatus
            message (str): Message object
        """
        # parse topic name from uri
        topic = re.search(r"\/(?:.(?!\/))+$", uri).group()[1:]
        topic = re.search(r".*#", topic).group()[:-1]

        # assign value from message
        # assumes message is of format {'health': {'remaining_life': 0, 'state': 3}} as defined by protobuf

        # value setting then being reset
        self.state["brake_pads.front"]["health"]["state"] = message.health.state
        self.state["brake_pads.rear"]["health"]["state"] = message.health.state

    @BaseService.RequestListener
    def ResetHealth(self, request, response):
        return self.handle_request(request, response)

    @BaseService.RequestListener
    def ManageHealthMonitoring(self, request, response):
        return self.handle_request(request, response)

    def handle_request(self, request, response):
        """
        Generic function for all braking RPC calls

        Args:
            request(protobuf): The protobuf containing the request object
            response(protobuf): The protobuf object returned as the response
        """
        try:
            self.validate_braking_req(request)
        except ValidationError as e:
            print(f"ValidationError: return code {e.code} with message {e.message}")
            response.code = e.code
            response.message = e.message
            # validation failed
            return response

            # validation passed
        response.code = 0
        response.message = "OK"

        self.publish_brake(request)
        return response

    def validate_braking_req(self, request):
        """
        Validates incoming requests for setting various brake settings. Raises an exception upon failure.

        Args:
            request(protobuf): the request object to be validated
        """
        # Reset Health Request
        if isinstance(request, ResetHealthRequest):
            if request.name not in ["brake_pads.front", "brake_pads.rear"]:
                raise ValidationError(12, f"Unsupported brake name: {request.name}")

            elif self.state[request.name]["health"]["state"] == HealthState.State.Value("S_UNSUPPORTED"):
                raise ValidationError(
                    2, f"Heath state for {request.name} set to " f"{self.state[request.name]['health']['state']}."
                )

            else:
                self.state[request.name]["name"] = request.name
                self.state[request.name]["health"]["remaining_life"] = 100
                self.state[request.name]["health"]["state"] = HealthState.State.Value("S_OK")

        # Manage Health Monitoring Request
        if isinstance(request, ManageHealthMonitoringRequest):
            if request.name not in ["brake_pads.front", "brake_pads.rear"]:
                raise ValidationError(12, f"Unsupported brake name: {request.name}")

            elif self.state["brake_pads.front"]["health"]["state"] == HealthState.State.Value("S_UNSUPPORTED") and self.state[
                "brake_pads.rear"
            ]["health"]["state"] == HealthState.State.Value("S_UNSUPPORTED"):
                raise ValidationError(2, "Health monitoring unsupported.")

            elif (
                self.state["brake_pads.front"]["health"]["state"] != HealthState.State.Value("S_DISABLED")
                or self.state["brake_pads.front"]["health"]["state"] != HealthState.State.Value("S_UNSUPPORTED")
                or self.state["brake_pads.rear"]["health"]["state"] != HealthState.State.Value("S_DISABLED")
                or self.state["brake_pads.rear"]["health"]["state"] != HealthState.State.Value("S_UNSUPPORTED")
            ) and request.is_enabled is False:
                self.state["brake_pads.front"]["health"]["state"] = HealthState.State.Value("S_DISABLED")
                self.state["brake_pads.rear"]["health"]["state"] = HealthState.State.Value("S_DISABLED")

            elif (
                self.state["brake_pads.front"]["health"]["state"] == HealthState.State.Value("S_DISABLED")
                or self.state["brake_pads.rear"]["health"]["state"] == HealthState.State.Value("S_DISABLED")
            ) and request.is_enabled is True:
                self.state["brake_pads.front"]["health"]["state"] = HealthState.State.Value("S_OK")
                self.state["brake_pads.rear"]["health"]["state"] = HealthState.State.Value("S_OK")

        return True

    def publish_brake(self, request):
        """
        Publishes a brake message based on the current state.

        Args:
            request(protobuf): the protobuf containing the rpc request
        """
        # publish brake info based on current state
        topic_prefix = KEY_URI_PREFIX + "/chassis.braking/1/"

        if isinstance(request, ResetHealthRequest):
            topic = topic_prefix + request.name + "#BrakePads"
            self.publish(topic, self.state[request.name], True)
        else:
            topic = topic_prefix + "brake_pads.front#BrakePads"
            self.publish(topic, self.state["brake_pads.front"], True)

            topic = topic_prefix + "brake_pads.rear#BrakePads"
            self.publish(topic, self.state["brake_pads.rear"], True)


class BrakingPreconditions(UListener):
    def __init__(self, braking_service):
        self.braking_service = braking_service

    def on_receive(self, umsg: UMessage):
        print("on receive braking called")
        print(umsg.payload)
        print(umsg.attributes.source)
        # parse data from here and pass it to onevent method
        pass

    def onEvent(self, uri, message):
        if message is not None:
            print(f"Received a {type(message)} message with value(s) {message}")
            self.braking_service.set_topic_state(uri, message)


if __name__ == "__main__":
    service = BrakingService()
    service.start()
