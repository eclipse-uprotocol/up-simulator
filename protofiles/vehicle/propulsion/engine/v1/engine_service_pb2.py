# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: vehicle/propulsion/engine/v1/engine_service.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.rpc import status_pb2 as google_dot_rpc_dot_status__pb2
import protofiles.uprotocol_options_pb2 as uprotocol__options__pb2
from protofiles.vehicle.propulsion.engine.v1 import engine_topics_pb2 as vehicle_dot_propulsion_dot_engine_dot_v1_dot_engine__topics__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n1vehicle/propulsion/engine/v1/engine_service.proto\x12\x1cvehicle.propulsion.engine.v1\x1a\x17google/rpc/status.proto\x1a\x17uprotocol_options.proto\x1a\x30vehicle/propulsion/engine/v1/engine_topics.proto\"\"\n\x12ResetHealthRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\"9\n\x13ResetHealthResponse\x12\"\n\x06status\x18\x01 \x01(\x0b\x32\x12.google.rpc.Status\"`\n\x10\x41irFilterOptions\x12\x46\n\x04name\x18\x01 \x01(\x0e\x32\x31.vehicle.propulsion.engine.v1.AirFilter.ResourcesB\x05\x82\xce\x18\x01*:\x04\xe0\xc7\x18\x00\"T\n\nOilOptions\x12@\n\x04name\x18\x01 \x01(\x0e\x32+.vehicle.propulsion.engine.v1.Oil.ResourcesB\x05\x82\xce\x18\x01*:\x04\xe0\xc7\x18\n\"\\\n\x0e\x43oolantOptions\x12\x44\n\x04name\x18\x01 \x01(\x0e\x32/.vehicle.propulsion.engine.v1.Coolant.ResourcesB\x05\x82\xce\x18\x01*:\x04\xe0\xc7\x18\x14\"d\n\x12\x45ngineStateOptions\x12H\n\x04name\x18\x01 \x01(\x0e\x32\x33.vehicle.propulsion.engine.v1.EngineState.ResourcesB\x05\x82\xce\x18\x01*:\x04\xe0\xc7\x18\x1e\x32\xa5\x01\n\x06\x45ngine\x12x\n\x0bResetHealth\x12\x30.vehicle.propulsion.engine.v1.ResetHealthRequest\x1a\x31.vehicle.propulsion.engine.v1.ResetHealthResponse\"\x04\xc0\xc1\x18\x01\x1a!\xa2\xbb\x18\x11propulsion.engine\xa8\xbb\x18\x01\xb0\xbb\x18\x00\xb8\xbb\x18\x13\x42\x34\n0org.covesa.uservice.vehicle.propulsion.engine.v1P\x01\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'vehicle.propulsion.engine.v1.engine_service_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n0org.covesa.uservice.vehicle.propulsion.engine.v1P\001'
  _AIRFILTEROPTIONS.fields_by_name['name']._options = None
  _AIRFILTEROPTIONS.fields_by_name['name']._serialized_options = b'\202\316\030\001*'
  _AIRFILTEROPTIONS._options = None
  _AIRFILTEROPTIONS._serialized_options = b'\340\307\030\000'
  _OILOPTIONS.fields_by_name['name']._options = None
  _OILOPTIONS.fields_by_name['name']._serialized_options = b'\202\316\030\001*'
  _OILOPTIONS._options = None
  _OILOPTIONS._serialized_options = b'\340\307\030\n'
  _COOLANTOPTIONS.fields_by_name['name']._options = None
  _COOLANTOPTIONS.fields_by_name['name']._serialized_options = b'\202\316\030\001*'
  _COOLANTOPTIONS._options = None
  _COOLANTOPTIONS._serialized_options = b'\340\307\030\024'
  _ENGINESTATEOPTIONS.fields_by_name['name']._options = None
  _ENGINESTATEOPTIONS.fields_by_name['name']._serialized_options = b'\202\316\030\001*'
  _ENGINESTATEOPTIONS._options = None
  _ENGINESTATEOPTIONS._serialized_options = b'\340\307\030\036'
  _ENGINE._options = None
  _ENGINE._serialized_options = b'\242\273\030\021propulsion.engine\250\273\030\001\260\273\030\000\270\273\030\023'
  _ENGINE.methods_by_name['ResetHealth']._options = None
  _ENGINE.methods_by_name['ResetHealth']._serialized_options = b'\300\301\030\001'
  _RESETHEALTHREQUEST._serialized_start=183
  _RESETHEALTHREQUEST._serialized_end=217
  _RESETHEALTHRESPONSE._serialized_start=219
  _RESETHEALTHRESPONSE._serialized_end=276
  _AIRFILTEROPTIONS._serialized_start=278
  _AIRFILTEROPTIONS._serialized_end=374
  _OILOPTIONS._serialized_start=376
  _OILOPTIONS._serialized_end=460
  _COOLANTOPTIONS._serialized_start=462
  _COOLANTOPTIONS._serialized_end=554
  _ENGINESTATEOPTIONS._serialized_start=556
  _ENGINESTATEOPTIONS._serialized_end=656
  _ENGINE._serialized_start=659
  _ENGINE._serialized_end=824
# @@protoc_insertion_point(module_scope)
