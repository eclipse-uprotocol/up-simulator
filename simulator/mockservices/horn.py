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

from simulator.utils.exceptions import ValidationError
from tdk.apis.apis import TdkApis
from tdk.core.abstract_service import BaseService
from tdk.helper.transport_configuration import TransportConfiguration
from tdk.target.protofiles.vehicle.body.horn.v1.horn_service_pb2 import (
    ActivateHornRequest,
    DeactivateHornRequest,
)
from tdk.target.protofiles.vehicle.body.horn.v1.horn_topics_pb2 import HornStatus
from tdk.utils.constant import KEY_URI_PREFIX


class HornService(BaseService):
    """
    The HornService object handles mock services for the horn lighting service
    """

    state = {}

    def __init__(self, portal_callback=None, transport_config: TransportConfiguration = None, tdk_apis: TdkApis = None):
        """
        HornService constructor:
        """

        super().__init__("body.horn", portal_callback, transport_config, tdk_apis)
        self.init_state()

    def init_state(self):
        """
        Initializes internal data structures for keeping track of the current state of the horn service
        """
        self.state["horn_status"] = self.init_message_state(HornStatus)

    @BaseService.request_listener
    def ActivateHorn(self, request, response):
        return self.handle_request(request, response)

    @BaseService.request_listener
    def DeactivateHorn(self, request, response):
        return self.handle_request(request, response)

    def handle_request(self, request, response):
        """
        Handles battery RPC calls

        Args:
            request(protobuf): The protobuf containing the request object
            response(protobuf): The protobuf object returned as the response
        """
        try:
            self.validate_horn_req(request)
        except ValidationError as e:
            print(f"ValidationError: return code {e.code} with message {e.message}")
            response.code = e.code
            response.message = e.message
            # validation failed
            return response

            # validation passed
        response.status.code = 0
        response.status.message = "OK"

        asyncio.create_task(self.publish_horn(request))
        return response

    def validate_horn_req(self, request):
        """
        Validates incoming requests for setting various horn settings. Raises an exception upon failure.

        Args:
            request(protobuf): the request object to be validated
        """

        if isinstance(request, ActivateHornRequest):
            pass

        if isinstance(request, DeactivateHornRequest):
            pass

    async def publish_horn(self, request):
        """
        Publishes a horn message based on the current state.

        Args:
        request(protobuf): the protobuf containing the rpc request
        """

        topic = KEY_URI_PREFIX + "/body.horn/1/horn#HornStatus"
        await self.publish(topic, self.state["horn_status"], True)
