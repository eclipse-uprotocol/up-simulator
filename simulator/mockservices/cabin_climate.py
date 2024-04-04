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

from google.protobuf.json_format import MessageToDict

from simulator.core.abstract_service import BaseService
from simulator.core.exceptions import ValidationError
from simulator.utils.constant import KEY_URI_PREFIX
from target.protofiles.vehicle.body.cabin_climate.v1 import cabin_climate_topics_pb2
from target.protofiles.vehicle.body.cabin_climate.v1.cabin_climate_service_pb2 import (
    SetTemperatureRequest,
    SetFanRequest,
    SetAirDistributionRequest,
    SetPowerRequest,
    SetLockRequest,
)


class CabinClimateService(BaseService):
    """
    The CabinClimateService object handles mock services for the cabin climate service
    """

    zone_names = []
    state = {}  # state for all zones
    settings_state = {}  # state for system settings

    def __init__(self, portal_callback=None):
        """
        CabinClimateService constructor
        """

        super().__init__("body.cabin_climate", portal_callback)

        self.init_state()

    def init_state(self):
        """
        Initializes internal data structures for keeping track of the current state of the cabin climate service
        """

        self.zone_names = [
            "row1",
            "row1_left",
            "row1_right",
            "row2",
            "row2_left",
            "row2_right",
            "row3",
            "row3_left",
            "row3_right",
        ]
        self.max = 31
        self.min = 16

        self.state = {}
        self.number_of_zones = 0
        for zone in self.zone_names:
            self.state[zone] = self.init_message_state(cabin_climate_topics_pb2.Zone)
            self.state[zone]["id"] = zone
        self.calc_number_of_zones()
        self.zone_names = set(self.zone_names)
        self.settings_state = self.init_message_state(cabin_climate_topics_pb2.SystemSettings)

    def calc_number_of_zones(self):
        self.number_of_zones = 0
        for zone in self.zone_names:
            zone_match = re.match(r"^zone\.row\d$", zone)
            if zone_match:
                self.number_of_zones += 1

    @BaseService.RequestListener
    def ExecuteClimateCommand(self, request, response):
        """
        Handles ExecuteClimateCommand RPC calls
        """
        # check zone id
        req_dict = MessageToDict(request.zone, including_default_value_fields=True)
        zone_str = req_dict["id"]
        try:
            self.validate_zone_req(request, zone_str)
        except ValidationError as e:
            response.code = e.code
            response.message = e.message
            # validation failed
            return response
        # validation passed
        response.code = 0
        response.message = "OK"
        # publish message from request data
        self.publish_synced_fields(request, zone_str)
        self.publish_zone(zone_str)

        return response

    @BaseService.RequestListener
    def UpdateSystemSettings(self, request, response):
        """
        Handles UpdateSystemSettings RPC calls
        """
        try:
            self.validate_settings_req(request)
        except ValidationError as e:
            response.code = e.code
            response.message = e.message
            # validation failed
            return response
        # validation passed
        response.code = 0
        response.message = "OK"
        self.publish_system_settings()
        return response

    @BaseService.RequestListener
    def SetTemperature(self, request, response):
        return self.handle_request(request, response)

    @BaseService.RequestListener
    def SetFan(self, request, response):
        return self.handle_request(request, response)

    @BaseService.RequestListener
    def SetAirDistribution(self, request, response):
        return self.handle_request(request, response)

    @BaseService.RequestListener
    def SetPower(self, request, response):
        return self.handle_request(request, response)

    @BaseService.RequestListener
    def SetLock(self, request, response):
        return self.handle_request(request, response)

    def handle_request(self, request, response):

        # handle SetTemperature request
        if isinstance(request, SetTemperatureRequest):
            # todo return SetTemperatureResponse response, Implement your logic here
            pass

        # handle SetFan request
        if isinstance(request, SetFanRequest):
            # todo return SetFanResponse response, Implement your logic here
            pass

        # handle SetAirDistribution request
        if isinstance(request, SetAirDistributionRequest):
            # todo return SetAirDistributionResponse response, Implement your logic here
            pass

        # handle SetPower request
        if isinstance(request, SetPowerRequest):
            # todo return SetPowerResponse response, Implement your logic here
            pass

        # handle SetLock request
        if isinstance(request, SetLockRequest):
            # todo return SetLockResponse response, Implement your logic here
            pass
        response.status.code = 0
        response.status.message = "OK"
        return response

    def normalize_field_mask(self, request, zone_str):
        """
        Normalizes the field mask and returns a new one
        """
        # check if all fields need updating or just fields in the field mask
        field_mask = request.update_mask.paths
        if field_mask == "Zone.*" or field_mask == "zone.*" or field_mask == "*":
            field_mask = []
        if len(field_mask) == 0:
            # update all fields by adding them to the field mask
            for field in self.state[zone_str].keys():
                # add "zone." prefix. this gets removed later, but services send this prefix
                field_mask.append("zone." + str(field))

        # remove "zone." prefix from field mask
        field_mask_normalized = []
        for field in field_mask:
            field = field.split(".")[1]
            field_mask_normalized.append(field)

        return field_mask_normalized

    def publish_synced_fields(self, request, zone_str):
        """
        If "blower_level", "air_distribution", "air_distribution_auto_state", or "auto_on" fields
        are sent with a resource of rowX_left, we need to publish on rowX_right as well.
        """
        groups = re.search(r"(row\d)_(left|right)", zone_str)
        if not groups:
            # if row is not _left or _right, exit
            return None
        row = groups.group(1)
        side = groups.group(2)
        mask = set(self.normalize_field_mask(request, zone_str))
        synced_fields = set(["blower_level", "air_distribution", "air_distribution_auto_state", "auto_on", "is_power_on"])
        fields_to_update = mask & synced_fields
        if fields_to_update:
            if side == "right":
                new_row = row + "_left"
            elif side == "left":
                new_row = row + "_right"
            for field in mask & synced_fields:
                self.state[new_row][field] = self.state[zone_str][field]
            self.publish_zone(new_row)

    def validate_zone_req(self, request, zone_str):
        """
        Validates incoming ExecuteClimateCommand requests. Raises an exception upon failure
        """

        # min/max values for various fields. in the future, the discovery service
        # will propigate these
        min_temp = int(self.min)
        max_temp = int(self.max)

        max_blower_level = 100
        min_blower_level = 0

        if zone_str not in self.zone_names:
            raise ValidationError(2, "Unsupported zone id.")

        field_mask_normalized = self.normalize_field_mask(request, zone_str)

        # loop through the field mask
        for field in field_mask_normalized:

            if self.state[zone_str]["is_power_on"] is False:
                # power is currently off
                fields_that_need_is_power_on = list(self.state[zone_str].keys())
                fields_that_need_is_power_on.remove("is_power_on")
                if field in fields_that_need_is_power_on:
                    # if not turning power on and using a field which needs the power on, fail
                    if not (("is_power_on" in field_mask_normalized) and (request.zone.is_power_on is True)):
                        raise ValidationError(9, f"Unable to set {field} when zone power is off.")

            # air_distribution_auto_state can only be AM_OFF or AM_AUTO when power is on.
            if field == "air_distribution_auto_state":
                if request.zone.air_distribution_auto_state not in [
                    cabin_climate_topics_pb2.AutomaticMode.Value("AM_AUTO"),
                    cabin_climate_topics_pb2.AutomaticMode.Value("AM_OFF"),
                ]:
                    raise ValidationError(
                        2,
                        f"Zone must be powered off to set air_distribution_auto_state to "
                        f"{request.zone.air_distribution_auto_state}.",
                    )

            # air_distribution cannot be AD_OFF, AD_AUTO, or AD_UNSPECIFIED when power is off
            if field == "air_distribution":
                air_distrib_valid_values = cabin_climate_topics_pb2.AirDistribution.values()
                air_distrib_valid_values.remove(cabin_climate_topics_pb2.AirDistribution.Value("AD_OFF"))
                air_distrib_valid_values.remove(cabin_climate_topics_pb2.AirDistribution.Value("AD_AUTO"))
                air_distrib_valid_values.remove(cabin_climate_topics_pb2.AirDistribution.Value("AD_UNSPECIFIED"))
                if request.zone.air_distribution not in air_distrib_valid_values:
                    raise ValidationError(
                        2,
                        f"Zone must be powered off to set air_distribution_auto_state to "
                        f"{request.zone.air_distribution_auto_state}.",
                    )

            # check temp in range
            if field == "temperature_setpoint":
                request.zone.temperature_setpoint = float(round(request.zone.temperature_setpoint))
                if (request.zone.temperature_setpoint > max_temp) or (request.zone.temperature_setpoint < min_temp):
                    raise ValidationError(2, "Temperature out of range.")

            # blower level in range
            if field == "blower_level":
                if (request.zone.blower_level > max_blower_level) or (request.zone.blower_level < min_blower_level):
                    raise ValidationError(2, "Blower level out of range.")

            # update state
            self.state[zone_str][field] = getattr(request.zone, field)

            # blower level needs a calculation
            if field == "blower_level":
                self.state[zone_str][field] = self.get_blower_level(self.state[zone_str][field])

        return True

    def publish_zone(self, zone_name):
        """
        Publishes a system settings message based on the current state
        """
        # publish zone info based on current state
        topic = KEY_URI_PREFIX + ":/body.cabin_climate/1/" + zone_name + "#Zone"
        self.publish(topic, self.state[zone_name], True)

    def get_est_cabin_temp(self):
        """
        Calculate the estimated_cabin_temperature
        """
        temp_sum = 0
        for zone in self.state.keys():
            # loop through all zones which have power on
            if self.state[zone]["is_power_on"]:
                temp_sum += self.state[zone]["temperature_setpoint"]
        return temp_sum / len(self.state.keys())

    def validate_settings_req(self, request):
        """
        Validates incoming UpdateSystemSettings requests. Raises an exception upon failure
        """
        # add all fields to the field mask if it's empty
        field_mask = request.update_mask.paths
        if field_mask == "Zone.*" or field_mask == "zone.*" or field_mask == "*":
            field_mask = []
        if len(field_mask) == 0:
            # update all fields
            for field in self.state.keys():
                field_mask.append("settings." + str(field))

        # loop through each field
        for field in field_mask:
            field = field.split(".")[1].strip()

            # override estimated_cabin_temperature with average of zone temps
            if field == "estimated_cabin_temperature":
                self.settings_state[field] = self.get_est_cabin_temp()
            if field == "ac_compressor_setting":
                if request.settings.ac_compressor_setting == cabin_climate_topics_pb2.SystemSettings.CompressorSetting.Value(
                    "CS_UNSPECIFIED"
                ):
                    raise ValidationError(2, "settings.ac_compressor_setting cannot be set to CS_UNSPECIFIED")
            if field == "heater_setting":
                if request.settings.heater_setting == cabin_climate_topics_pb2.SystemSettings.HeaterSetting.Value(
                    "HS_UNSPECIFIED"
                ):
                    raise ValidationError(2, "settings.heater_setting cannot be set to HS_UNSPECIFIED")

            if self.number_of_zones < 2:
                if field == "sync_all" or field == "sync_rear_to_driver" or field == "rear_zone_lockout":
                    raise ValidationError(
                        2,
                        "sync_all, sync_rear_to_driver, and rear_zone_lockout are not available " "when there is only 1 zone.",
                    )
            if self.number_of_zones < 3:
                if field == "sync_3rdRow_to_driver" or field == "third_row_zone_lockout":
                    raise ValidationError(
                        2, "sync_3rdRow_to_driver and third_row_zone_lockout are not available when " "there is no third row."
                    )

            self.settings_state[field] = getattr(request.settings, field)

    def publish_system_settings(self):
        """
        Publishes a system settings message based on the current state
        """
        topic = KEY_URI_PREFIX + ":/body.cabin_climate/1/system_settings#SystemSettings"
        # publish system settings based on current state
        self.publish(topic, self.settings_state, True)

    def get_blower_level(self, number):
        """
        Calculates the blower level
        """
        if number > 0:
            blower_level = int(round(number / 12.5))
            val = int(round((blower_level / 8) * 100))
            return val
        else:
            return 0

    def disableAllZones(self):
        self.zone_names = set([])
        self.number_of_zones = 0

    def enableAllZones(self):
        self.init_state()

    def enableZone(self, zone_name):
        if zone_name not in self.zone_names:
            self.zone_names.add(zone_name)
            zone_match = re.match(r"^zone\.row\d$", zone_name)
            if zone_match:
                subzones = [zone_name + "_left", zone_name + "_right"]
                for subzone in subzones:
                    self.zone_names.add(subzone)

        self.calc_number_of_zones()

    def disableZone(self, zone_name):
        if zone_name in self.zone_names:
            self.zone_names.remove(zone_name)
            zone_match = re.match(r"^zone\.row\d$", zone_name)
            if zone_match:
                subzones = [zone_name + "_left", zone_name + "_right"]
                for subzone in subzones:
                    self.zone_names.remove(subzone)

        self.calc_number_of_zones()


if __name__ == "__main__":
    service = CabinClimateService()
    service.start()
