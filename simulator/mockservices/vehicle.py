# Copyright (C) GM Global Technology Operations LLC 2022-2023.
# All Rights Reserved.
# GM Confidential Restricted.

import re

from simulator.target.protofiles.vehicle.v1.vehicle_service_pb2 import ResetTripMeterRequest, SetTransportModeRequest
from simulator.target.protofiles.vehicle.v1.vehicle_topics_pb2 import TripMeter, VehicleUsage
from uprotocol.proto.umessage_pb2 import UMessage
from uprotocol.transport.ulistener import UListener

from simulator.core.abstract_service import BaseService
from simulator.core.exceptions import ValidationError
from simulator.utils.constant import KEY_URI_PREFIX


class VehicleService(BaseService):
    """
    The Vehicle object handles mock services for the vehicle service
    """

    state = {}

    def __init__(self, portal_callback=None):
        """
        VehicleService constructor:
        """

        super().__init__(
            "vehicle",
            portal_callback,
        )
        self.init_state()

    def start_rpc_service(self):
        status = super().start_rpc_service()
        if status:
            self.subscribe(
                [
                    KEY_URI_PREFIX + "/vehicle/1/trip_meter.trip_1#TripMeter",
                    KEY_URI_PREFIX + "/vehicle/1/trip_meter.trip_2#TripMeter",
                    KEY_URI_PREFIX + "/vehicle/1/vehicle_usage.transport_mode#VehicleUsage",
                ],
                VehiclePreconditions(self),
            )
        return status

    def init_state(self):
        """
        Initializes internal data structures for keeping track of the current state of the trip meter service
        """
        self.state = {}

        # add trip values
        for trip in TripMeter.Resources.keys():
            self.state[trip] = self.init_message_state(TripMeter)
            self.state[trip]["name"] = trip

        # add transport mode state
        for mode in VehicleUsage.Resources.keys():
            self.state[mode] = self.init_message_state(VehicleUsage)

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
        # assumes message is of format {'is_operation_allowed': true} as defined by protobuf
        print(f"Topic name: {topic}")

        if isinstance(message, TripMeter):
            self.state[topic]["value"] = message.value
        if isinstance(message, VehicleUsage):
            self.state["transport_mode"]["is_setting_change_allowed"] = message.is_setting_change_allowed
            self.state["transport_mode"]["is_active"] = message.is_active

    @BaseService.RequestListener
    def ResetTripMeter(self, request, response):
        return self.handle_request(request, response)

    @BaseService.RequestListener
    def SetTransportMode(self, request, response):
        return self.handle_request(request, response)

    def handle_request(self, request, response):
        """
        Handles vehicle RPC calls

        Args:
            request(protobuf): The protobuf containing the request object
            response(protobuf): The protobuf object returned as the response
        """
        try:
            self.validate_vehicle_req(request)
        except ValidationError as e:
            print(f"ValidationError: return code {e.code} with message {e.message}")
            response.code = e.code
            response.message = e.message
            # validation failed
            return response

            # validation passed
        response.code = 0
        response.message = "OK"

        self.publish_vehicle(request)
        return response

    def validate_vehicle_req(self, request):
        """
        Validates incoming requests for setting various vehicle settings. Raises an exception upon failure.

        Args:
            request(protobuf): the request object to be validated
        """
        # Request Trip Meter Request
        if isinstance(request, ResetTripMeterRequest):
            if request.trip_meter not in TripMeter.Resources.values():
                raise ValidationError(12, f"Unsupported trip meter name {request.trip_meter}.")
            elif request.trip_meter == TripMeter.Resources.Value("trip_1"):
                self.state["trip_1"]["value"] = float(0)
            elif request.trip_meter == TripMeter.Resources.Value("trip_2"):
                self.state["trip_2"]["value"] = float(0)

        # Set Transport Mode Request
        elif isinstance(request, SetTransportModeRequest):
            if not self.state["transport_mode"]["is_setting_change_allowed"]:
                raise ValidationError(
                    9,
                    f"Failed precondition value: is_setting_change_allowed is "
                    f"{self.state['transport_mode']['is_setting_change_allowed']} when should be "
                    f"True.",
                )
            else:
                self.state["transport_mode"]["is_active"] = request.is_active

        return True

    def publish_vehicle(self, request):
        """
        Publishes a vehicle message based on the current state.

        Args:
        request(protobuf): the protobuf containing the rpc request
        """
        if isinstance(request, ResetTripMeterRequest):
            # get trip_meter key from value, expecting 0 - trip_1 or 1 - trip_2
            trip_val = list(TripMeter.Resources.keys())[list(TripMeter.Resources.values()).index(request.trip_meter)]
            topic = KEY_URI_PREFIX + "/vehicle/1/trip_meter." + trip_val + "#TripMeter"
            self.publish(topic, self.state[trip_val], True)

        if isinstance(request, SetTransportModeRequest):
            topic = KEY_URI_PREFIX + "/vehicle/1/vehicle_usage.transport_mode#VehicleUsage"
            self.publish(topic, self.state, True)

        return True


class VehiclePreconditions(UListener):
    def __init__(self, vehicle_service):
        self.vehicle_service = vehicle_service

    def on_receive(self, umsg: UMessage):
        print("on receive vehicle service called")
        print(umsg.payload)
        print(umsg.attributes.source)
        # parse data from here and pass it to onevent method
        pass

    def onEvent(self, uri, message):
        if message is not None:
            print(f"Recieved a {type(message)} message with value(s) {message}")
            self.vehicle_service.set_topic_state(uri, message)


if __name__ == "__main__":
    service = VehicleService()
    service.start()
