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


from simulator.core.abstract_service import BaseService

from target.protofiles.vehicle.body.mirrors.v1.mirrors_service_pb2 import (SlideSideMirrorRequest,
                                                                           FoldSideMirrorRequest,
                                                                           UnfoldSideMirrorRequest,
                                                                           TiltSideMirrorRequest,
                                                                           UntiltSideMirrorRequest,
                                                                           ActivateHeatedSideMirrorRequest,
                                                                           DeactivateHeatedSideMirrorRequest,
                                                                           UpdateSideMirrorMovementSettingsRequest,
                                                                           UpdateHeatedSideMirrorsSettingsRequest)


class BodyMirrorsService(BaseService):

    def __init__(self, portal_callback=None):
        """
        BodyMirrorsService constructor
        """
        super().__init__('body.mirrors', portal_callback)
        self.init_state()

    def init_state(self):
        """
        Initializes internal data structures for keeping track of the current state of the BodyMirrorsService
        """
        self.state = {}

    # RPC Request Listeners for each RPC method
    @BaseService.RequestListener
    def SlideSideMirror(self, request, response):
        return self.handle_request(request, response)

    @BaseService.RequestListener
    def FoldSideMirror(self, request, response):
        return self.handle_request(request, response)

    @BaseService.RequestListener
    def UnfoldSideMirror(self, request, response):
        return self.handle_request(request, response)

    @BaseService.RequestListener
    def TiltSideMirror(self, request, response):
        return self.handle_request(request, response)

    @BaseService.RequestListener
    def UntiltSideMirror(self, request, response):
        return self.handle_request(request, response)

    @BaseService.RequestListener
    def ActivateHeatedSideMirror(self, request, response):
        return self.handle_request(request, response)

    @BaseService.RequestListener
    def DeactivateHeatedSideMirror(self, request, response):
        return self.handle_request(request, response)

    @BaseService.RequestListener
    def UpdateSideMirrorMovementSettings(self, request, response):
        return self.handle_request(request, response)

    @BaseService.RequestListener
    def UpdateHeatedSideMirrorsSettings(self, request, response):
        return self.handle_request(request, response)

    def handle_request(self, request, response):

        # handle SlideSideMirror request       
        if type(request) == SlideSideMirrorRequest:
            # todo return SlideSideMirrorResponse response, Implement your logic here
            pass

        # handle FoldSideMirror request       
        if type(request) == FoldSideMirrorRequest:
            # todo return FoldSideMirrorResponse response, Implement your logic here
            pass

        # handle UnfoldSideMirror request       
        if type(request) == UnfoldSideMirrorRequest:
            # todo return UnfoldSideMirrorResponse response, Implement your logic here
            pass

        # handle TiltSideMirror request       
        if type(request) == TiltSideMirrorRequest:
            # todo return TiltSideMirrorResponse response, Implement your logic here
            pass

        # handle UntiltSideMirror request       
        if type(request) == UntiltSideMirrorRequest:
            # todo return UntiltSideMirrorResponse response, Implement your logic here
            pass

        # handle ActivateHeatedSideMirror request       
        if type(request) == ActivateHeatedSideMirrorRequest:
            # todo return ActivateHeatedSideMirrorResponse response, Implement your logic here
            pass

        # handle DeactivateHeatedSideMirror request       
        if type(request) == DeactivateHeatedSideMirrorRequest:
            # todo return DeactivateHeatedSideMirrorResponse response, Implement your logic here
            pass

        # handle UpdateSideMirrorMovementSettings request       
        if type(request) == UpdateSideMirrorMovementSettingsRequest:
            # todo return UpdateSideMirrorMovementSettingsResponse response, Implement your logic here
            pass

        # handle UpdateHeatedSideMirrorsSettings request       
        if type(request) == UpdateHeatedSideMirrorsSettingsRequest:
            # todo return UpdateHeatedSideMirrorsSettingsResponse response, Implement your logic here
            pass
        response.code.code = 0
        response.code.message = "OK"
        return response


if __name__ == "__main__":
    service = BodyMirrorsService()
    service.start()
