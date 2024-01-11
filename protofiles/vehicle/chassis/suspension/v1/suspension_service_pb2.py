# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: vehicle/chassis/suspension/v1/suspension_service.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.rpc import status_pb2 as google_dot_rpc_dot_status__pb2
import uprotocol_options_pb2 as uprotocol__options__pb2
import protofiles.uservices_options_pb2 as uservices__options__pb2
from protofiles.vehicle.chassis.suspension.v1 import suspension_topics_pb2 as vehicle_dot_chassis_dot_suspension_dot_v1_dot_suspension__topics__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n6vehicle/chassis/suspension/v1/suspension_service.proto\x12\x1dvehicle.chassis.suspension.v1\x1a\x17google/rpc/status.proto\x1a\x17uprotocol_options.proto\x1a\x17uservices_options.proto\x1a\x35vehicle/chassis/suspension/v1/suspension_topics.proto\"\x85\x04\n\x14SetRideHeightRequest\x12J\n\x07\x63ommand\x18\x01 \x01(\x0e\x32\x39.vehicle.chassis.suspension.v1.RideHeight.RideHeightLevel\x12g\n\x0cmotion_speed\x18\x02 \x01(\x0e\x32\x46.vehicle.chassis.suspension.v1.SetRideHeightRequest.MotionSpeedCommandB\x04\xd0\x8c\x19\x01H\x00\x88\x01\x01\x12\x65\n\x0bmotion_type\x18\x03 \x01(\x0e\x32\x45.vehicle.chassis.suspension.v1.SetRideHeightRequest.MotionTypeCommandB\x04\xd0\x8c\x19\x01H\x01\x88\x01\x01\"R\n\x12MotionSpeedCommand\x12\x13\n\x0fMSC_UNSPECIFIED\x10\x00\x12\x0c\n\x08MSC_SLOW\x10\x01\x12\x0c\n\x08MSC_FAST\x10\x02\x12\x0b\n\x07MSC_MED\x10\x03\"\\\n\x11MotionTypeCommand\x12\x13\n\x0fMTC_UNSPECIFIED\x10\x00\x12\x12\n\x0eMTC_CONCURRENT\x10\x01\x12\x0f\n\x0bMTC_RATCHET\x10\x02\x12\r\n\tMTC_CAMEL\x10\x03\x42\x0f\n\r_motion_speedB\x0e\n\x0c_motion_type\";\n\x15SetRideHeightResponse\x12\"\n\x06status\x18\x01 \x01(\x0b\x32\x12.google.rpc.Status\"l\n\x11RideHeightOptions\x12Q\n\rresource_name\x18\x01 \x01(\x0e\x32\x33.vehicle.chassis.suspension.v1.RideHeight.ResourcesB\x05\x82\xce\x18\x01*:\x04\xe0\xc7\x18\n\"\x84\x01\n\x1dRideHeightSystemStatusOptions\x12]\n\rresource_name\x18\x01 \x01(\x0e\x32?.vehicle.chassis.suspension.v1.RideHeightSystemStatus.ResourcesB\x05\x82\xce\x18\x01*:\x04\xe0\xc7\x18\x14\x32\xb3\x01\n\nSuspension\x12\x80\x01\n\rSetRideHeight\x12\x33.vehicle.chassis.suspension.v1.SetRideHeightRequest\x1a\x34.vehicle.chassis.suspension.v1.SetRideHeightResponse\"\x04\xc0\xc1\x18\x01\x1a\"\xa2\xbb\x18\x12\x63hassis.suspension\xa8\xbb\x18\x01\xb0\xbb\x18\x00\xb8\xbb\x18\x15\x42\x35\n1org.covesa.uservice.vehicle.chassis.suspension.v1P\x01\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'vehicle.chassis.suspension.v1.suspension_service_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n1org.covesa.uservice.vehicle.chassis.suspension.v1P\001'
  _SETRIDEHEIGHTREQUEST.fields_by_name['motion_speed']._options = None
  _SETRIDEHEIGHTREQUEST.fields_by_name['motion_speed']._serialized_options = b'\320\214\031\001'
  _SETRIDEHEIGHTREQUEST.fields_by_name['motion_type']._options = None
  _SETRIDEHEIGHTREQUEST.fields_by_name['motion_type']._serialized_options = b'\320\214\031\001'
  _RIDEHEIGHTOPTIONS.fields_by_name['resource_name']._options = None
  _RIDEHEIGHTOPTIONS.fields_by_name['resource_name']._serialized_options = b'\202\316\030\001*'
  _RIDEHEIGHTOPTIONS._options = None
  _RIDEHEIGHTOPTIONS._serialized_options = b'\340\307\030\n'
  _RIDEHEIGHTSYSTEMSTATUSOPTIONS.fields_by_name['resource_name']._options = None
  _RIDEHEIGHTSYSTEMSTATUSOPTIONS.fields_by_name['resource_name']._serialized_options = b'\202\316\030\001*'
  _RIDEHEIGHTSYSTEMSTATUSOPTIONS._options = None
  _RIDEHEIGHTSYSTEMSTATUSOPTIONS._serialized_options = b'\340\307\030\024'
  _SUSPENSION._options = None
  _SUSPENSION._serialized_options = b'\242\273\030\022chassis.suspension\250\273\030\001\260\273\030\000\270\273\030\025'
  _SUSPENSION.methods_by_name['SetRideHeight']._options = None
  _SUSPENSION.methods_by_name['SetRideHeight']._serialized_options = b'\300\301\030\001'
  _SETRIDEHEIGHTREQUEST._serialized_start=220
  _SETRIDEHEIGHTREQUEST._serialized_end=737
  _SETRIDEHEIGHTREQUEST_MOTIONSPEEDCOMMAND._serialized_start=528
  _SETRIDEHEIGHTREQUEST_MOTIONSPEEDCOMMAND._serialized_end=610
  _SETRIDEHEIGHTREQUEST_MOTIONTYPECOMMAND._serialized_start=612
  _SETRIDEHEIGHTREQUEST_MOTIONTYPECOMMAND._serialized_end=704
  _SETRIDEHEIGHTRESPONSE._serialized_start=739
  _SETRIDEHEIGHTRESPONSE._serialized_end=798
  _RIDEHEIGHTOPTIONS._serialized_start=800
  _RIDEHEIGHTOPTIONS._serialized_end=908
  _RIDEHEIGHTSYSTEMSTATUSOPTIONS._serialized_start=911
  _RIDEHEIGHTSYSTEMSTATUSOPTIONS._serialized_end=1043
  _SUSPENSION._serialized_start=1046
  _SUSPENSION._serialized_end=1225
# @@protoc_insertion_point(module_scope)
