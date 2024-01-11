# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: vehicle/chassis/braking/v1/braking_service.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.rpc import status_pb2 as google_dot_rpc_dot_status__pb2
import uprotocol_options_pb2 as uprotocol__options__pb2
from protofiles.vehicle.chassis.braking.v1 import braking_topics_pb2 as vehicle_dot_chassis_dot_braking_dot_v1_dot_braking__topics__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n0vehicle/chassis/braking/v1/braking_service.proto\x12\x1avehicle.chassis.braking.v1\x1a\x17google/rpc/status.proto\x1a\x17uprotocol_options.proto\x1a/vehicle/chassis/braking/v1/braking_topics.proto\"\"\n\x12ResetHealthRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\"A\n\x1dManageHealthMonitoringRequest\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x12\n\nis_enabled\x18\x02 \x01(\x08\"i\n\x11\x42rakePedalOptions\x12N\n\rresource_name\x18\x01 \x01(\x0e\x32\x30.vehicle.chassis.braking.v1.BrakePedal.ResourcesB\x05\x82\xce\x18\x01*:\x04\xe0\xc7\x18\x00\"r\n\x10\x42rakePadsOptions\x12X\n\rresource_name\x18\x01 \x01(\x0e\x32/.vehicle.chassis.braking.v1.BrakePads.ResourcesB\x10\x82\xce\x18\x0c\x62rake_pads.*:\x04\xe0\xc7\x18\n2\xf2\x01\n\x07\x42raking\x12W\n\x0bResetHealth\x12..vehicle.chassis.braking.v1.ResetHealthRequest\x1a\x12.google.rpc.Status\"\x04\xc0\xc1\x18\x01\x12m\n\x16ManageHealthMonitoring\x12\x39.vehicle.chassis.braking.v1.ManageHealthMonitoringRequest\x1a\x12.google.rpc.Status\"\x04\xc0\xc1\x18\x02\x1a\x1f\xa2\xbb\x18\x0f\x63hassis.braking\xa8\xbb\x18\x01\xb0\xbb\x18\x00\xb8\xbb\x18\x11\x42*\n&org.covesa.uservice.chassis.braking.v1P\x01\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'vehicle.chassis.braking.v1.braking_service_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n&org.covesa.uservice.chassis.braking.v1P\001'
  _BRAKEPEDALOPTIONS.fields_by_name['resource_name']._options = None
  _BRAKEPEDALOPTIONS.fields_by_name['resource_name']._serialized_options = b'\202\316\030\001*'
  _BRAKEPEDALOPTIONS._options = None
  _BRAKEPEDALOPTIONS._serialized_options = b'\340\307\030\000'
  _BRAKEPADSOPTIONS.fields_by_name['resource_name']._options = None
  _BRAKEPADSOPTIONS.fields_by_name['resource_name']._serialized_options = b'\202\316\030\014brake_pads.*'
  _BRAKEPADSOPTIONS._options = None
  _BRAKEPADSOPTIONS._serialized_options = b'\340\307\030\n'
  _BRAKING._options = None
  _BRAKING._serialized_options = b'\242\273\030\017chassis.braking\250\273\030\001\260\273\030\000\270\273\030\021'
  _BRAKING.methods_by_name['ResetHealth']._options = None
  _BRAKING.methods_by_name['ResetHealth']._serialized_options = b'\300\301\030\001'
  _BRAKING.methods_by_name['ManageHealthMonitoring']._options = None
  _BRAKING.methods_by_name['ManageHealthMonitoring']._serialized_options = b'\300\301\030\002'
  _RESETHEALTHREQUEST._serialized_start=179
  _RESETHEALTHREQUEST._serialized_end=213
  _MANAGEHEALTHMONITORINGREQUEST._serialized_start=215
  _MANAGEHEALTHMONITORINGREQUEST._serialized_end=280
  _BRAKEPEDALOPTIONS._serialized_start=282
  _BRAKEPEDALOPTIONS._serialized_end=387
  _BRAKEPADSOPTIONS._serialized_start=389
  _BRAKEPADSOPTIONS._serialized_end=503
  _BRAKING._serialized_start=506
  _BRAKING._serialized_end=748
# @@protoc_insertion_point(module_scope)
