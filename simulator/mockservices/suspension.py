"""
SPDX-FileCopyrightText: Copyright (c) 2024 Contributors to the Eclipse Foundation

See the NOTICE file(s) distributed with this work for additional
information regarding copyright ownership.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
SPDX-FileType: SOURCE
SPDX-License-Identifier: Apache-2.0
"""

import asyncio
import re

from uprotocol.proto.umessage_pb2 import UMessage
from uprotocol.transport.ulistener import UListener

from simulator.utils.exceptions import ValidationError
from tdk.apis.apis import TdkApis
from tdk.core.abstract_service import BaseService
from tdk.helper.transport_configuration import TransportConfiguration
from tdk.target.protofiles.vehicle.chassis.suspension.v1.suspension_service_pb2 import SetRideHeightRequest
from tdk.target.protofiles.vehicle.chassis.suspension.v1.suspension_topics_pb2 import (
    RideHeight,
    RideHeightSystemStatus,
)
from tdk.utils.constant import KEY_URI_PREFIX


class SuspensionService(BaseService):
    """
    The SuspensionService object handles mock services for the sound service
    """

    state = {}

    def __init__(self, portal_callback=None, transport_config: TransportConfiguration = None, tdk_apis: TdkApis = None):
        """
        SuspensionService constructor:
        """
        # todo: move uninstall to BaseService class

        super().__init__("chassis.suspension", portal_callback, transport_config, tdk_apis)
        self.init_state()

    async def subscribe(self):
        await super().subscribe(
            [
                KEY_URI_PREFIX + "/chassis.suspension/1/ride_height_system_status#RideHeightSystemStatus",
            ],
            SuspensionPreconditions(self),
        )

    def init_state(self):
        self.state = {}

        for ride_height in RideHeight.Resources.keys():
            self.state[ride_height] = self.init_message_state(RideHeight)
            self.state[ride_height]["name"] = ride_height

        for status in RideHeightSystemStatus.Resources.keys():
            self.state[status] = self.init_message_state(RideHeightSystemStatus)
            self.state[status]["name"] = status

        self.state["preconditions"] = {}

        # populate supported and available heights
        heights = [x for x in range(1, 13)]
        self.state["ride_height"]["supported_heights"] = heights
        self.state["ride_height"]["available_heights"] = heights

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
        # assumes message is of format {'source': 'S_APP'} as defined by protobuf
        if "ride_height_system_status" in topic:
            self.state[topic]["source"] = message.source

    @BaseService.request_listener
    def SetRideHeight(self, request, response):
        return self.handle_request(request, response)

    def handle_precondition(self, condition, value):
        """
        Handles preconditions set by feature file and passed from BDD

        Args:
            condition(string): corresponds to a condition listed by a feature file and sets it in state
            value(any): corresponds to a condition's value listed by a feature file and sets it in state
        """
        self.state["preconditions"][condition] = value

    def handle_request(self, request, response):
        """
        Handles suspension RPC calls

        Args:
            request(protobuf): The protobuf containing the request object
            response(protobuf): The protobuf object returned as the response
        """
        try:
            self.validate_suspension_req(request)
        except ValidationError as e:
            print(f"ValidationError: return code {e.code} with message {e.message}")
            response.status.code = e.code
            response.status.message = e.message
            # validation failed
            return response

        # validation passed
        response.status.code = 0
        response.status.message = "OK"

        asyncio.create_task(self.publish_suspension())
        return response

    def validate_suspension_req(self, request):
        """
        Validates incoming requests for setting various suspension settings. Raises an exception upon failure.

        Args:
            request(protobuf): the request object to be validated
        """

        # check command value
        if request.command not in RideHeight.RideHeightLevel.values():
            raise ValidationError(12, "Command value not supported.")

        # Set Ride Height Request
        elif isinstance(request, SetRideHeightRequest):
            # handle preconditions passed through bdd

            if "ride height external control status" in self.state["preconditions"]:
                if self.state["preconditions"]["ride height external control status"] == "active":
                    if self.state["ride_height_system_status"]["source"] == RideHeightSystemStatus.Source.Value(
                        "S_USER"
                    ):
                        self.state["ride_height"]["target_height"] = request.command
                        self.state["ride_height"]["current_height"] = request.command

                    elif self.state["ride_height_system_status"]["source"] == RideHeightSystemStatus.Source.Value(
                        "S_APP"
                    ):
                        if request.command == RideHeight.RideHeightLevel.Value("RHL_UNSPECIFIED"):
                            raise ValidationError(3, "Command value unspecified.")
                        elif request.command in self.state["ride_height"]["supported_heights"]:
                            self.state["ride_height"]["target_height"] = request.command
                            self.state["ride_height"]["current_height"] = request.command

                            if request.motion_speed != SetRideHeightRequest.MotionSpeedCommand.Value("MSC_UNSPECIFIED"):
                                self.state["ride_height"]["motion_speed"] = request.motion_speed
                            if request.motion_type != SetRideHeightRequest.MotionTypeCommand.Value("MTC_UNSPECIFIED"):
                                self.state["ride_height"]["motion_type"] = request.motion_type

                elif self.state["preconditions"]["ride height external control status"] == "Temporary Inhibit":
                    raise ValidationError(10, "Value is not supported")

                elif self.state["preconditions"]["ride height external control status"] == "Internally Arbitrated":
                    raise ValidationError(10, "Value is not supported")

                elif self.state["preconditions"]["ride height external control status"] == "Failed":
                    raise ValidationError(1, "Cannot happen.")

            else:
                if request.command in self.state["ride_height"]["supported_heights"]:
                    self.state["ride_height"]["target_height"] = request.command
                    self.state["ride_height"]["current_height"] = request.command
                if request.motion_speed != SetRideHeightRequest.MotionSpeedCommand.Value("MSC_UNSPECIFIED"):
                    self.state["ride_height"]["motion_speed"] = request.motion_speed
                if request.motion_type != SetRideHeightRequest.MotionTypeCommand.Value("MTC_UNSPECIFIED"):
                    self.state["ride_height"]["motion_type"] = request.motion_type

        return True

    async def publish_suspension(self):
        """
        Publishes a suspension message based on the current state.

        Args:
        request(protobuf): the protobuf containing the rpc request
        """
        topic = KEY_URI_PREFIX + "/chassis.suspension/1/ride_height#RideHeight"

        await self.publish(topic, self.state["ride_height"], True)


class SuspensionPreconditions(UListener):
    def __init__(self, suspension_service):
        self.suspension_service = suspension_service

    async def on_receive(self, umsg: UMessage):
        print("on receive suspension called")
        print(umsg.payload)
        print(umsg.attributes.source)
        # parse data from here and pass it to onevent method
        pass

    def onEvent(self, uri, message):
        if message is not None:
            print(f"Received a {type(message)} message with value(s) {message}")
            self.suspension_service.set_topic_state(uri, message)
