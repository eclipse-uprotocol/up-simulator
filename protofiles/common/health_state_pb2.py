# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: common/health_state.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x19\x63ommon/health_state.proto\x12\x06\x63ommon\"\xed\x01\n\x0bHealthState\x12\x1b\n\x0eremaining_life\x18\x01 \x01(\x05H\x00\x88\x01\x01\x12(\n\x05state\x18\x02 \x01(\x0e\x32\x19.common.HealthState.State\"\x83\x01\n\x05State\x12\x11\n\rS_UNSPECIFIED\x10\x00\x12\x08\n\x04S_OK\x10\x01\x12\x12\n\x0eS_SERVICE_SOON\x10\x02\x12\x11\n\rS_SERVICE_NOW\x10\x03\x12\x0e\n\nS_DISABLED\x10\x04\x12\x13\n\x0fS_FAULT_PRESENT\x10\x05\x12\x11\n\rS_UNSUPPORTED\x10\x06\x42\x11\n\x0f_remaining_lifeB\x1e\n\x1aorg.covesa.uservice.commonP\x01\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'common.health_state_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n\032org.covesa.uservice.commonP\001'
  _HEALTHSTATE._serialized_start=38
  _HEALTHSTATE._serialized_end=275
  _HEALTHSTATE_STATE._serialized_start=125
  _HEALTHSTATE_STATE._serialized_end=256
# @@protoc_insertion_point(module_scope)