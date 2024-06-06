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

from simulator.core.abstract_service import BaseService
from simulator.target.protofiles.vehicle.propulsion.engine.v1.engine_service_pb2 import (
    ResetHealthRequest,
)


class EngineService(BaseService):
    def __init__(self, portal_callback=None):
        """
        EngineService constructor
        """
        super().__init__("propulsion.engine", portal_callback)
        self.init_state()

    def init_state(self):
        """
        Initializes internal data structures for keeping track of the current state of the EngineService
        """
        self.state = {}

    # RPC Request Listeners for each RPC method
    @BaseService.request_listener
    def ResetHealth(self, request, response):
        return self.handle_request(request, response)

    def handle_request(self, request, response):
        # handle ResetHealth request
        if isinstance(request, ResetHealthRequest):
            # todo return ResetHealthResponse response, Implement your logic here
            pass
        response.status.code = 0
        response.status.message = "OK"
        return response


if __name__ == "__main__":
    service = EngineService()
    service.start()
