# Copyright (C) GM Global Technology Operations LLC 2022-2023.
# All Rights Reserved.
# GM Confidential Restricted.

from simulator.core.abstract_service import BaseService
from simulator.core.exceptions import ValidationError
from simulator.utils.constant import KEY_URI_PREFIX
from target.protofiles.vehicle.body.horn.v1.horn_service_pb2 import (
    ActivateHornRequest,
    DeactivateHornRequest,
)
from target.protofiles.vehicle.body.horn.v1.horn_topics_pb2 import HornStatus


class HornService(BaseService):
    """
    The HornService object handles mock services for the horn lighting service
    """

    state = {}

    def __init__(self, portal_callback=None):
        """
        HornService constructor:
        """

        super().__init__("body.horn", portal_callback)
        self.init_state()

    def init_state(self):
        """
        Initializes internal data structures for keeping track of the current state of the horn service
        """
        self.state["horn_status"] = self.init_message_state(HornStatus)

    @BaseService.RequestListener
    def ActivateHorn(self, request, response):
        return self.handle_request(request, response)

    @BaseService.RequestListener
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

        self.publish_horn(request)
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

    def publish_horn(self, request):
        """
        Publishes a horn message based on the current state.

        Args:
        request(protobuf): the protobuf containing the rpc request
        """

        topic = KEY_URI_PREFIX + "/body.horn/1/horn#HornStatus"
        self.publish(topic, self.state["horn_status"], True)
