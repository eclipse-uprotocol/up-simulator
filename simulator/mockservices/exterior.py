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


class VehicleExteriorService(BaseService):
    def __init__(self, portal_callback=None):
        """
        VehicleExteriorService constructor
        """
        super().__init__('vehicle.exterior', portal_callback)
        self.init_state()

    def init_state(self):
        """
        Initializes internal data structures for keeping track of the current state of the VehicleExteriorService
        """
        self.state = {}

    # RPC Request Listeners for each RPC method
    def handle_request(self, request, response):
        return response


if __name__ == "__main__":
    service = VehicleExteriorService()
    service.start()
