# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: vehicle/exterior/v1/exterior_topics.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import uservices_options_pb2 as uservices__options__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n)vehicle/exterior/v1/exterior_topics.proto\x12\x13vehicle.exterior.v1\x1a\x17uservices_options.proto\"u\n\x10SolarInformation\x12&\n\x0flight_intensity\x18\x01 \x01(\x05\x42\x08\xc8\x8c\x19\x01\xd8\x8c\x19\x12H\x00\x88\x01\x01\"%\n\tResources\x12\x18\n\x14\x65xterior_environment\x10\x00\x42\x12\n\x10_light_intensity\"p\n\x0bTemperature\x12&\n\x0f\x61ir_temperature\x18\x01 \x01(\x02\x42\x08\xc8\x8c\x19\x01\xd8\x8c\x19\x03H\x00\x88\x01\x01\"%\n\tResources\x12\x18\n\x14\x65xterior_environment\x10\x00\x42\x12\n\x10_air_temperature\"\x8f\x01\n\x0c\x41mbientLight\x12\x14\n\x06is_day\x18\x01 \x01(\x08\x42\x04\xc8\x8c\x19\x01\x12*\n\x13\x61mbient_light_level\x18\x02 \x01(\x05\x42\x08\xc8\x8c\x19\x01\xd8\x8c\x19\x14H\x00\x88\x01\x01\"%\n\tResources\x12\x18\n\x14\x65xterior_environment\x10\x00\x42\x16\n\x14_ambient_light_levelB+\n\'org.covesa.uservice.vehicle.exterior.v1P\x01\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'vehicle.exterior.v1.exterior_topics_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n\'org.covesa.uservice.vehicle.exterior.v1P\001'
  _SOLARINFORMATION.fields_by_name['light_intensity']._options = None
  _SOLARINFORMATION.fields_by_name['light_intensity']._serialized_options = b'\310\214\031\001\330\214\031\022'
  _TEMPERATURE.fields_by_name['air_temperature']._options = None
  _TEMPERATURE.fields_by_name['air_temperature']._serialized_options = b'\310\214\031\001\330\214\031\003'
  _AMBIENTLIGHT.fields_by_name['is_day']._options = None
  _AMBIENTLIGHT.fields_by_name['is_day']._serialized_options = b'\310\214\031\001'
  _AMBIENTLIGHT.fields_by_name['ambient_light_level']._options = None
  _AMBIENTLIGHT.fields_by_name['ambient_light_level']._serialized_options = b'\310\214\031\001\330\214\031\024'
  _SOLARINFORMATION._serialized_start=91
  _SOLARINFORMATION._serialized_end=208
  _SOLARINFORMATION_RESOURCES._serialized_start=151
  _SOLARINFORMATION_RESOURCES._serialized_end=188
  _TEMPERATURE._serialized_start=210
  _TEMPERATURE._serialized_end=322
  _TEMPERATURE_RESOURCES._serialized_start=151
  _TEMPERATURE_RESOURCES._serialized_end=188
  _AMBIENTLIGHT._serialized_start=325
  _AMBIENTLIGHT._serialized_end=468
  _AMBIENTLIGHT_RESOURCES._serialized_start=151
  _AMBIENTLIGHT_RESOURCES._serialized_end=188
# @@protoc_insertion_point(module_scope)