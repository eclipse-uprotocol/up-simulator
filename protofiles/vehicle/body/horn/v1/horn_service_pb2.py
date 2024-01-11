# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: vehicle/body/horn/v1/horn_service.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.rpc import status_pb2 as google_dot_rpc_dot_status__pb2
import uprotocol_options_pb2 as uprotocol__options__pb2
from protofiles.vehicle.body.horn.v1 import horn_topics_pb2 as vehicle_dot_body_dot_horn_dot_v1_dot_horn__topics__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\'vehicle/body/horn/v1/horn_service.proto\x12\x14vehicle.body.horn.v1\x1a\x17google/rpc/status.proto\x1a\x17uprotocol_options.proto\x1a&vehicle/body/horn/v1/horn_topics.proto\"x\n\x13\x41\x63tivateHornRequest\x12,\n\x04mode\x18\x01 \x01(\x0e\x32\x1e.vehicle.body.horn.v1.HornMode\x12\x33\n\x07\x63ommand\x18\x02 \x03(\x0b\x32\".vehicle.body.horn.v1.HornSequence\":\n\x14\x41\x63tivateHornResponse\x12\"\n\x06status\x18\x01 \x01(\x0b\x32\x12.google.rpc.Status\"\x17\n\x15\x44\x65\x61\x63tivateHornRequest\"<\n\x16\x44\x65\x61\x63tivateHornResponse\x12\"\n\x06status\x18\x01 \x01(\x0b\x32\x12.google.rpc.Status\"c\n\x11HornStatusOptions\x12H\n\rresource_name\x18\x01 \x01(\x0e\x32*.vehicle.body.horn.v1.HornStatus.ResourcesB\x05\x82\xce\x18\x01*:\x04\xe0\xc7\x18\x00\x32\x81\x02\n\x04Horn\x12k\n\x0c\x41\x63tivateHorn\x12).vehicle.body.horn.v1.ActivateHornRequest\x1a*.vehicle.body.horn.v1.ActivateHornResponse\"\x04\xc0\xc1\x18\x01\x12q\n\x0e\x44\x65\x61\x63tivateHorn\x12+.vehicle.body.horn.v1.DeactivateHornRequest\x1a,.vehicle.body.horn.v1.DeactivateHornResponse\"\x04\xc0\xc1\x18\x02\x1a\x19\xa2\xbb\x18\tbody.horn\xa8\xbb\x18\x01\xb0\xbb\x18\x01\xb8\xbb\x18\x1c\x42,\n(org.covesa.uservice.vehicle.body.horn.v1P\x01\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'vehicle.body.horn.v1.horn_service_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n(org.covesa.uservice.vehicle.body.horn.v1P\001'
  _HORNSTATUSOPTIONS.fields_by_name['resource_name']._options = None
  _HORNSTATUSOPTIONS.fields_by_name['resource_name']._serialized_options = b'\202\316\030\001*'
  _HORNSTATUSOPTIONS._options = None
  _HORNSTATUSOPTIONS._serialized_options = b'\340\307\030\000'
  _HORN._options = None
  _HORN._serialized_options = b'\242\273\030\tbody.horn\250\273\030\001\260\273\030\001\270\273\030\034'
  _HORN.methods_by_name['ActivateHorn']._options = None
  _HORN.methods_by_name['ActivateHorn']._serialized_options = b'\300\301\030\001'
  _HORN.methods_by_name['DeactivateHorn']._options = None
  _HORN.methods_by_name['DeactivateHorn']._serialized_options = b'\300\301\030\002'
  _ACTIVATEHORNREQUEST._serialized_start=155
  _ACTIVATEHORNREQUEST._serialized_end=275
  _ACTIVATEHORNRESPONSE._serialized_start=277
  _ACTIVATEHORNRESPONSE._serialized_end=335
  _DEACTIVATEHORNREQUEST._serialized_start=337
  _DEACTIVATEHORNREQUEST._serialized_end=360
  _DEACTIVATEHORNRESPONSE._serialized_start=362
  _DEACTIVATEHORNRESPONSE._serialized_end=422
  _HORNSTATUSOPTIONS._serialized_start=424
  _HORNSTATUSOPTIONS._serialized_end=523
  _HORN._serialized_start=526
  _HORN._serialized_end=783
# @@protoc_insertion_point(module_scope)
