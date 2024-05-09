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


from uprotocol.uri.factory.uentity_factory import UEntityFactory

mock_entity = []


def stop_service(name):
    for index, entity_dict in enumerate(mock_entity):
        if entity_dict.get("name") == name:
            entity_dict.get("entity").disconnect()
            mock_entity.pop(index)
            break


def get_service_instance_from_entity(name):
    for index, entity_dict in enumerate(mock_entity):
        if entity_dict.get('name') == name:
            return entity_dict.get('entity')
    return None


def get_all_running_service():
    running_service = []
    for index, entity_dict in enumerate(mock_entity):
        running_service.append(entity_dict.get('name'))
    return running_service


def start_service(entity, callback):
    global service

    if entity == "chassis.braking":
        from simulator.mockservices.braking import BrakingService

        service = BrakingService(callback)
    elif entity == "body.cabin_climate":
        from simulator.mockservices.cabin_climate import CabinClimateService

        service = CabinClimateService(callback)
    elif entity == "chassis":
        from simulator.mockservices.chassis import ChassisService

        service = ChassisService(callback)
    elif entity == "propulsion.engine":
        from simulator.mockservices.engine import EngineService

        service = EngineService(callback)
    elif entity == "vehicle.exterior":
        from simulator.mockservices.exterior import VehicleExteriorService

        service = VehicleExteriorService(callback)
    elif entity == "example.hello_world":
        from simulator.mockservices.hello_world import HelloWorldService

        service = HelloWorldService(callback)
    elif entity == "body.horn":
        from simulator.mockservices.horn import HornService

        service = HornService(callback)
    elif entity == "body.mirrors":
        from simulator.mockservices.mirrors import BodyMirrorsService

        service = BodyMirrorsService(callback)
    elif entity == "chassis.suspension":
        from simulator.mockservices.suspension import SuspensionService

        service = SuspensionService(callback)
    elif entity == "propulsion.transmission":
        from simulator.mockservices.transmission import TransmissionService

        service = TransmissionService(callback)
    elif entity == "vehicle":
        from simulator.mockservices.vehicle import VehicleService

        service = VehicleService(callback)
    elif entity == "body.seating":
        from simulator.mockservices.seating import SeatingService

        service = SeatingService(callback)

    if service is not None and service.start():
        mock_entity.append({"name": entity, "entity": service})
        return True
    else:
        return False


def get_entity_from_descriptor(entity_descriptor):
    return UEntityFactory.from_proto(entity_descriptor)
