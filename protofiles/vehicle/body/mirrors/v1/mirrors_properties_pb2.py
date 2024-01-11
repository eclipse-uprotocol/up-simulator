# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: vehicle/body/mirrors/v1/mirrors_properties.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import descriptor_pb2 as google_dot_protobuf_dot_descriptor__pb2
import protofiles.uservices_options_pb2 as uservices__options__pb2
import protofiles.units_pb2 as units__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n0vehicle/body/mirrors/v1/mirrors_properties.proto\x12\x17vehicle.body.mirrors.v1\x1a google/protobuf/descriptor.proto\x1a\x17uservices_options.proto\x1a\x0bunits.proto:K\n\x1dis_power_side_mirrors_present\x12\x1f.google.protobuf.ServiceOptions\x18\xec\xad\x03 \x01(\x08\x88\x01\x01:G\n\x19is_heated_mirrors_present\x12\x1f.google.protobuf.ServiceOptions\x18\xed\xad\x03 \x01(\x08\x88\x01\x01:V\n)vehicle_speed_inhibiting_side_mirror_fold\x12\x1e.google.protobuf.MethodOptions\x18\xee\xad\x03 \x01(\x05\x88\x01\x01:_\n2is_side_mirrors_auto_unfold_based_on_vehicle_speed\x12\x1e.google.protobuf.MethodOptions\x18\xef\xad\x03 \x01(\x08\x88\x01\x01:\\\n)vehicle_speed_inhibiting_side_mirror_tilt\x12\x1e.google.protobuf.MethodOptions\x18\xf0\xad\x03 \x01(\x05\x42\x04\xd8\x8c\x19\x01\x88\x01\x01:_\n2is_side_mirrors_auto_untilt_based_on_vehicle_speed\x12\x1e.google.protobuf.MethodOptions\x18\xf1\xad\x03 \x01(\x08\x88\x01\x01:U\n\"maximum_time_side_mirror_is_tilted\x12\x1e.google.protobuf.MethodOptions\x18\xf2\xad\x03 \x01(\x05\x42\x04\xd8\x8c\x19\x17\x88\x01\x01\x42/\n+org.covesa.uservice.vehicle.body.mirrors.v1P\x01\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'vehicle.body.mirrors.v1.mirrors_properties_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:
  google_dot_protobuf_dot_descriptor__pb2.ServiceOptions.RegisterExtension(is_power_side_mirrors_present)
  google_dot_protobuf_dot_descriptor__pb2.ServiceOptions.RegisterExtension(is_heated_mirrors_present)
  google_dot_protobuf_dot_descriptor__pb2.MethodOptions.RegisterExtension(vehicle_speed_inhibiting_side_mirror_fold)
  google_dot_protobuf_dot_descriptor__pb2.MethodOptions.RegisterExtension(is_side_mirrors_auto_unfold_based_on_vehicle_speed)
  google_dot_protobuf_dot_descriptor__pb2.MethodOptions.RegisterExtension(vehicle_speed_inhibiting_side_mirror_tilt)
  google_dot_protobuf_dot_descriptor__pb2.MethodOptions.RegisterExtension(is_side_mirrors_auto_untilt_based_on_vehicle_speed)
  google_dot_protobuf_dot_descriptor__pb2.MethodOptions.RegisterExtension(maximum_time_side_mirror_is_tilted)

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'\n+org.covesa.uservice.vehicle.body.mirrors.v1P\001'
  vehicle_speed_inhibiting_side_mirror_tilt._options = None
  vehicle_speed_inhibiting_side_mirror_tilt._serialized_options = b'\330\214\031\001'
  maximum_time_side_mirror_is_tilted._options = None
  maximum_time_side_mirror_is_tilted._serialized_options = b'\330\214\031\027'
# @@protoc_insertion_point(module_scope)
