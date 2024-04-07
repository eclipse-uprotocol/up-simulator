from uprotocol.uri.factory.uentity_factory import UEntityFactory
from uprotocol.proto.uri_pb2 import UEntity, UResource
from uprotocol.proto.uprotocol_options_pb2 import name as Name
from uprotocol.proto.uprotocol_options_pb2 import (
    version_major as Version_Major,
)
from uprotocol.proto.uprotocol_options_pb2 import (
    version_minor as Version_Minor,
)
from uprotocol.proto.uprotocol_options_pb2 import id as Id
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

    if service is not None:
        service.start()
        mock_entity.append({"name": entity, "entity": service})

def get_entity_from_descriptor(entity_descriptor):
    return UEntityFactory.from_proto(entity_descriptor)

