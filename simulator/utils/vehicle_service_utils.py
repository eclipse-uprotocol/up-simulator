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

try:
    from tdk.helper import someip_helper
except Exception:
    pass

mock_entity = []


def stop_service(name):
    for index, entity_dict in enumerate(mock_entity):
        if entity_dict.get("name") == name:
            entity_dict.get("entity").disconnect()
            mock_entity.pop(index)
            break


def remove_service_from_someip(name):
    for index, entity_name in enumerate(someip_helper.temp_someip_entity):
        if entity_name == name:
            someip_helper.temp_someip_entity.pop(index)
            stop_service(name)
            break


def get_service_instance_from_entity(name):
    for index, entity_dict in enumerate(mock_entity):
        if entity_dict.get("name") == name:
            return entity_dict.get("entity")
    return None


def get_all_running_service():
    running_service = []
    for index, entity_dict in enumerate(mock_entity):
        running_service.append(entity_dict.get("name"))
    return running_service


def get_all_configured_someip_service():
    configured_service = []
    for entity_name in someip_helper.someip_entity:
        configured_service.append(entity_name)
    return configured_service


async def start_service(entity, callback, transport_config, tdk_apis):
    global service
    service = None

    if entity == "chassis.braking":
        from simulator.mockservices.braking import BrakingService

        service = BrakingService(callback, transport_config, tdk_apis)
    elif entity == "body.cabin_climate":
        from simulator.mockservices.cabin_climate import CabinClimateService

        service = CabinClimateService(callback, transport_config, tdk_apis)
    elif entity == "chassis":
        from simulator.mockservices.chassis import ChassisService

        service = ChassisService(callback, transport_config, tdk_apis)
    elif entity == "propulsion.engine":
        from simulator.mockservices.engine import EngineService

        service = EngineService(callback, transport_config, tdk_apis)
    elif entity == "vehicle.exterior":
        from simulator.mockservices.exterior import VehicleExteriorService

        service = VehicleExteriorService(callback, transport_config, tdk_apis)
    elif entity == "example.hello_world":
        from simulator.mockservices.hello_world import HelloWorldService

        service = HelloWorldService(callback, transport_config, tdk_apis)
    elif entity == "body.horn":
        from simulator.mockservices.horn import HornService

        service = HornService(callback, transport_config, tdk_apis)
    elif entity == "body.mirrors":
        from simulator.mockservices.mirrors import BodyMirrorsService

        service = BodyMirrorsService(callback, transport_config, tdk_apis)
    elif entity == "chassis.suspension":
        from simulator.mockservices.suspension import SuspensionService

        service = SuspensionService(callback, transport_config, tdk_apis)
    elif entity == "propulsion.transmission":
        from simulator.mockservices.transmission import TransmissionService

        service = TransmissionService(callback, transport_config, tdk_apis)
    elif entity == "vehicle":
        from simulator.mockservices.vehicle import VehicleService

        service = VehicleService(callback, transport_config, tdk_apis)
    elif entity == "body.seating":
        from simulator.mockservices.seating import SeatingService

        service = SeatingService(callback, transport_config, tdk_apis)

    if service is None:
        return "Not found"

    if await service.start():
        mock_entity.append({"name": entity, "entity": service})
        return "Running"
    else:
        return "Error"
