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

from uprotocol.proto.uattributes_pb2 import UAttributes
from uprotocol.proto.upayload_pb2 import UPayload
from uprotocol.proto.uri_pb2 import UUri
from uprotocol.proto.ustatus_pb2 import UStatus
from uprotocol.transport.ulistener import UListener

from simulator.core.abstract_service import BaseService
from simulator.core.exceptions import ValidationError
from target.protofiles.vehicle.chassis.v1.chassis_service_pb2 import (UpdateTireRequest, )
from target.protofiles.vehicle.chassis.v1.chassis_topics_pb2 import (Tire, )


class ChassisService(BaseService):
    """
    The ChassisService object handles mock services for the chassis service
    """

    # valid tire names
    tire_names = []
    timeout = 9  # timeout time in seconds for discovery service

    state = {}

    def __init__(self, portal_callback=None):

        super().__init__("chassis", portal_callback)
        self.init_state()

    def start_rpc_service(self):
        super().start_rpc_service()
        self.subscribe(["up:/chassis/1/tire.front_left#Tire", "up:/chassis/1/tire.front_right#Tire",
                        "up:/chassis/1/tire.rear_right#Tire", "up:/chassis/1/tire.rear_left#Tire",
                        "up:/chassis/1/tire.rear_left_inner#Tire",
                        "up:/chassis/1/tire.rear_right_inner#Tire", ], ChassisPreconditions(self))
    def init_state(self):
        """
        Initializes internal data structures for keeping track of the current state of the tire update service
        """
        self.state = {}

        for tire in Tire.Resources.keys():
            tire = 'tire.' + tire
            self.tire_names.append(tire)

        for tire in self.tire_names:
            self.state[tire] = self.init_message_state(Tire)
            self.state[tire]['resource_name'] = tire

    ###Topic Name grabs From the Environment.py Finds the Messages to the Ubus Leak State and So on
    def set_topic_state(self, uri, message):
        """
        Sets state dictionary with values passed by the uBus, overwritting default values assigned during initialization

        Args:
            uri (str): String to identify specific car component eg.
            message (str): Message object
        """
        # parse topic name from uri
        topic = re.search(r'\/(?:.(?!\/))+$', uri).group()[1:]
        topic = re.search(r'.*#', topic).group()[:-1]

        # assign value from message
        # assumes message is of format {'leak_state': true} as defined by protobuf
        self.state[topic]['leak_state'] = message.leak_state
        self.state[topic]['is_leak_detection_enabled'] = message.is_leak_detection_enabled

    @BaseService.RequestListener
    def UpdateTire(self, request, response):
        """
        Handles UpdateTire RPC Calls. Protobuf needs to be updated to add "Tire.Resources resource_name" attribute to 
        UpdateTireRequest
        """
        try:
            self.validate_tire(request)
        except ValidationError as e:
            # validation failed
            response.code = e.code
            response.message = e.message
            return response

        # validation passed
        response.code = 0
        response.message = "OK"
        self.publish_tire(request)
        return response

    def validate_tire(self, request):
        if type(request) == UpdateTireRequest:
            for tire in self.tire_names:
                # TestCase_02
                if self.state[tire]["leak_state"] not in [Tire.TireLeakState.Value("TLS_NO_LEAK"),
                                                          Tire.TireLeakState.Value("TLS_UNSPECIFIED")] and \
                        self.state[tire]["is_leak_detection_enabled"] == True:
                    self.state[tire]["is_leak_present"] = True
                    self.state[tire]["leak_state"] = Tire.TireLeakState.Value("TLS_NO_LEAK")

                # Testcase_03
                elif self.state[tire][
                    "leak_state"] in Tire.TireLeakState.values() and request.is_leak_present == False and \
                        self.state[tire]["is_leak_detection_enabled"] == False:
                    self.state[tire]["is_leak_present"] = False

                # Testcase_04
                elif self.state[tire]["is_leak_detection_enabled"] == False and request.is_leak_present == True:
                    self.state[tire]["is_leak_present"] = True
                    self.state[tire]["is_leak_notification_enabled"] = True
                    raise ValidationError(2, f"is_leak_detection_enabled: False")

                # Testcase_05
                elif (self.state[tire][
                          "is_leak_detection_enabled"] == False and request.is_leak_notification_enabled == True and
                      request.is_leak_present == True):
                    self.state[tire]["is_leak_present"] = True
                    self.state[tire]["is_leak_notification_enabled"] = True
                    raise ValidationError(2, f"is_leak_detection_enabled: False")

                # Testcase_01
                else:
                    self.state[tire]["is_leak_detection_enabled"] = request.is_leak_notification_enabled

        return True

    def publish_tire(self, request):
        """
        Publishes a message based on the current tire
        """
        for tire in self.tire_names:
            topic = "up:/chassis/1/" + tire + "#Tire"
            self.publish(topic, self.state[tire],True)


class ChassisPreconditions(UListener):
    def __init__(self, covesa_service):
        self.covesa_Service = covesa_service

    def on_receive(self, topic: UUri, payload: UPayload, attributes: UAttributes) -> UStatus:
        print('on recieve called')
        print(payload)
        print(topic)
        print(attributes)
        # parse data from here and pass it to onevent method
        pass

    def onEvent(self, uri, message):
        if message is not None:
            print(f"Received a {type(message)} message with value {message}")
            self.covesa_Service.set_topic_state(uri, message)


if __name__ == "__main__":
    service = ChassisService()
    service.start()
