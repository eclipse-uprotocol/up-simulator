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


from simulator.core.abstract_service import CovesaService


class TransmissionService(CovesaService):

    def __init__(self, portal_callback=None):
        """
        TransmissionService constructor
        """
        super().__init__('propulsion.transmission', portal_callback)
        self.init_state()

    def init_state(self):
        """
        Initializes internal data structures for keeping track of the current state of the TransmissionService
        """
        self.state = {}

    # RPC Request Listeners for each RPC method
    def handle_request(self, request, response):
        return response


if __name__ == "__main__":
    service = TransmissionService()
    service.start()
