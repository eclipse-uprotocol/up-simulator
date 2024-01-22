# Copyright (C) GM Global Technology Operations LLC 2022-2023.
# All Rights Reserved.
# GM Confidential Restricted.

import re

from target.protofiles.vehicle.v1.vehicle_topics_pb2 import (TripMeter, VehicleUsage)
from uprotocol.proto.uattributes_pb2 import UAttributes
from uprotocol.proto.upayload_pb2 import UPayload
from uprotocol.proto.uri_pb2 import UUri
from uprotocol.proto.ustatus_pb2 import UStatus
from uprotocol.transport.ulistener import UListener

from simulator.core.abstract_service import CovesaService
from simulator.core.exceptions import ValidationError
from target.protofiles.vehicle.v1.vehicle_service_pb2 import (ResetTripMeterRequest, SetTransportModeRequest)


class VehicleService(CovesaService):
    """
    The Vehicle object handles mock services for the vehicle service
    """

    state = {}

    def __init__(self, portal_callback=None):
        """
        VehicleService constructor:
        """

        super().__init__("vehicle", portal_callback, )
        self.init_state()
        self.subscribe(
            ["up:/vehicle/1/trip_meter.trip_1#TripMeter", "up:/vehicle/1/trip_meter.trip_2#TripMeter",
             "up:/vehicle/1/vehicle_usage.transport_mode#VehicleUsage", ], VehiclePreconditions(self))

    def init_state(self):
        """
        Initializes internal data structures for keeping track of the current state of the trip meter service
        """
        self.state = {}

        # add trip values
        for trip in TripMeter.Resources.keys():
            self.state[trip] = self.init_message_state(TripMeter)
            self.state[trip]['name'] = trip

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
        topic = re.search(r'\/(?:.(?!\/))+$', uri).group()[1:]
        topic = re.search(r'.*#', topic).group()[:-1]

        # assign value from message
        # assumes message is of format {'is_operation_allowed': true} as defined by protobuf
        print(f"Topic name: {topic}")

        if type(message) == TripMeter:
            self.state[topic]['value'] = message.value
        if type(message) == VehicleUsage:
            self.state["transport_mode"]['is_setting_change_allowed'] = message.is_setting_change_allowed
            self.state["transport_mode"]['is_active'] = message.is_active

    @CovesaService.RequestListener
    def ResetTripMeter(self, request, response):
        return self.handle_request(request, response)

    @CovesaService.RequestListener
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
        if type(request) == ResetTripMeterRequest:
            if request.trip_meter not in TripMeter.Resources.values():
                raise ValidationError(12, f"Unsupported trip meter name {request.trip_meter}.")
            elif request.trip_meter == TripMeter.Resources.Value("trip_1"):
                self.state["trip_1"]["value"] = float(0)
            elif request.trip_meter == TripMeter.Resources.Value("trip_2"):
                self.state["trip_2"]["value"] = float(0)

        # Set Transport Mode Request
        elif type(request) == SetTransportModeRequest:
            if not self.state["transport_mode"]["is_setting_change_allowed"]:
                raise ValidationError(9, f"Failed precondition value: is_setting_change_allowed is "
                                         f"{self.state['transport_mode']['is_setting_change_allowed']} when should be "
                                         f"True.")
            else:
                self.state["transport_mode"]["is_active"] = request.is_active

        return True

    def publish_vehicle(self, request):
        """
        Publishes a vehicle message based on the current state.

        Args:
        request(protobuf): the protobuf containing the rpc request
        """
        if type(request) == ResetTripMeterRequest:
            # get trip_meter key from value, expecting 0 - trip_1 or 1 - trip_2
            trip_val = list(TripMeter.Resources.keys())[list(TripMeter.Resources.values()).index(request.trip_meter)]
            topic = "up:/vehicle/1/trip_meter." + trip_val + "#TripMeter"
            self.publish(topic, self.state[trip_val])

        if type(request) == SetTransportModeRequest:
            topic = "up:/vehicle/1/vehicle_usage.transport_mode#VehicleUsage"
            self.publish(topic, self.state)

        return True


class VehiclePreconditions(UListener):
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
        if message != None:
            print(f"Recieved a {type(message)} message with value(s) {message}")
            self.covesa_Service.set_topic_state(uri, message)


if __name__ == "__main__":
    service = VehicleService()
    service.start()
