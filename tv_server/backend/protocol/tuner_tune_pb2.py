# Generated by the protocol buffer compiler.  DO NOT EDIT!

from google.protobuf import descriptor
from google.protobuf import message
from google.protobuf import reflection
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)



DESCRIPTOR = descriptor.FileDescriptor(
  name='tuner_tune.proto',
  package='tvserver',
  serialized_pb='\n\x10tuner_tune.proto\x12\x08tvserver\"\xa2\x04\n\ntuner_tune\x12\x0f\n\x07version\x18\x01 \x02(\r\x12\x14\n\x0ctuning_bigid\x18\x02 \x01(\t\x12=\n\x0eparameter_type\x18\x03 \x01(\x0e\x32%.tvserver.tuner_tune.parameter_type_e\x12\x31\n\x08vchannel\x18\x04 \x01(\x0b\x32\x1f.tvserver.tuner_tune.vchannel_m\x12H\n\x13\x63hannelsconf_record\x18\x05 \x01(\x0b\x32+.tvserver.tuner_tune.channels_conf_record_m\x12-\n\x06target\x18\x06 \x01(\x0b\x32\x1d.tvserver.tuner_tune.target_m\x1a\x1e\n\nvchannel_m\x12\x10\n\x08vchannel\x18\x01 \x01(\r\x1a\x85\x01\n\x16\x63hannels_conf_record_m\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x11\n\tfrequency\x18\x02 \x01(\r\x12\x12\n\nmodulation\x18\x03 \x01(\t\x12\x10\n\x08video_id\x18\x04 \x01(\r\x12\x10\n\x08\x61udio_id\x18\x05 \x01(\r\x12\x12\n\nprogram_id\x18\x06 \x01(\r\x1a&\n\x08target_m\x12\x0c\n\x04host\x18\x01 \x01(\t\x12\x0c\n\x04port\x18\x02 \x01(\x05\"2\n\x10parameter_type_e\x12\x0c\n\x08VCHANNEL\x10\x00\x12\x10\n\x0c\x43HANNELSCONF\x10\x01')



_TUNER_TUNE_PARAMETER_TYPE_E = descriptor.EnumDescriptor(
  name='parameter_type_e',
  full_name='tvserver.tuner_tune.parameter_type_e',
  filename=None,
  file=DESCRIPTOR,
  values=[
    descriptor.EnumValueDescriptor(
      name='VCHANNEL', index=0, number=0,
      options=None,
      type=None),
    descriptor.EnumValueDescriptor(
      name='CHANNELSCONF', index=1, number=1,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=527,
  serialized_end=577,
)


_TUNER_TUNE_VCHANNEL_M = descriptor.Descriptor(
  name='vchannel_m',
  full_name='tvserver.tuner_tune.vchannel_m',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='vchannel', full_name='tvserver.tuner_tune.vchannel_m.vchannel', index=0,
      number=1, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=319,
  serialized_end=349,
)

_TUNER_TUNE_CHANNELS_CONF_RECORD_M = descriptor.Descriptor(
  name='channels_conf_record_m',
  full_name='tvserver.tuner_tune.channels_conf_record_m',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='name', full_name='tvserver.tuner_tune.channels_conf_record_m.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='frequency', full_name='tvserver.tuner_tune.channels_conf_record_m.frequency', index=1,
      number=2, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='modulation', full_name='tvserver.tuner_tune.channels_conf_record_m.modulation', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='video_id', full_name='tvserver.tuner_tune.channels_conf_record_m.video_id', index=3,
      number=4, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='audio_id', full_name='tvserver.tuner_tune.channels_conf_record_m.audio_id', index=4,
      number=5, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='program_id', full_name='tvserver.tuner_tune.channels_conf_record_m.program_id', index=5,
      number=6, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=352,
  serialized_end=485,
)

_TUNER_TUNE_TARGET_M = descriptor.Descriptor(
  name='target_m',
  full_name='tvserver.tuner_tune.target_m',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='host', full_name='tvserver.tuner_tune.target_m.host', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='port', full_name='tvserver.tuner_tune.target_m.port', index=1,
      number=2, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=487,
  serialized_end=525,
)

_TUNER_TUNE = descriptor.Descriptor(
  name='tuner_tune',
  full_name='tvserver.tuner_tune',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='version', full_name='tvserver.tuner_tune.version', index=0,
      number=1, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='tuning_bigid', full_name='tvserver.tuner_tune.tuning_bigid', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='parameter_type', full_name='tvserver.tuner_tune.parameter_type', index=2,
      number=3, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='vchannel', full_name='tvserver.tuner_tune.vchannel', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='channelsconf_record', full_name='tvserver.tuner_tune.channelsconf_record', index=4,
      number=5, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='target', full_name='tvserver.tuner_tune.target', index=5,
      number=6, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_TUNER_TUNE_VCHANNEL_M, _TUNER_TUNE_CHANNELS_CONF_RECORD_M, _TUNER_TUNE_TARGET_M, ],
  enum_types=[
    _TUNER_TUNE_PARAMETER_TYPE_E,
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=31,
  serialized_end=577,
)

_TUNER_TUNE_VCHANNEL_M.containing_type = _TUNER_TUNE;
_TUNER_TUNE_CHANNELS_CONF_RECORD_M.containing_type = _TUNER_TUNE;
_TUNER_TUNE_TARGET_M.containing_type = _TUNER_TUNE;
_TUNER_TUNE.fields_by_name['parameter_type'].enum_type = _TUNER_TUNE_PARAMETER_TYPE_E
_TUNER_TUNE.fields_by_name['vchannel'].message_type = _TUNER_TUNE_VCHANNEL_M
_TUNER_TUNE.fields_by_name['channelsconf_record'].message_type = _TUNER_TUNE_CHANNELS_CONF_RECORD_M
_TUNER_TUNE.fields_by_name['target'].message_type = _TUNER_TUNE_TARGET_M
_TUNER_TUNE_PARAMETER_TYPE_E.containing_type = _TUNER_TUNE;
DESCRIPTOR.message_types_by_name['tuner_tune'] = _TUNER_TUNE

class tuner_tune(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  
  class vchannel_m(message.Message):
    __metaclass__ = reflection.GeneratedProtocolMessageType
    DESCRIPTOR = _TUNER_TUNE_VCHANNEL_M
    
    # @@protoc_insertion_point(class_scope:tvserver.tuner_tune.vchannel_m)
  
  class channels_conf_record_m(message.Message):
    __metaclass__ = reflection.GeneratedProtocolMessageType
    DESCRIPTOR = _TUNER_TUNE_CHANNELS_CONF_RECORD_M
    
    # @@protoc_insertion_point(class_scope:tvserver.tuner_tune.channels_conf_record_m)
  
  class target_m(message.Message):
    __metaclass__ = reflection.GeneratedProtocolMessageType
    DESCRIPTOR = _TUNER_TUNE_TARGET_M
    
    # @@protoc_insertion_point(class_scope:tvserver.tuner_tune.target_m)
  DESCRIPTOR = _TUNER_TUNE
  
  # @@protoc_insertion_point(class_scope:tvserver.tuner_tune)

# @@protoc_insertion_point(module_scope)