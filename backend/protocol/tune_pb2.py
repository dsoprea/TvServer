# Generated by the protocol buffer compiler.  DO NOT EDIT!

from google.protobuf import descriptor
from google.protobuf import message
from google.protobuf import reflection
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)



DESCRIPTOR = descriptor.FileDescriptor(
  name='tune.proto',
  package='tvserver',
  serialized_pb='\n\ntune.proto\x12\x08tvserver\"8\n\x13tune_param_vchannel\x12\x0f\n\x07version\x18\x01 \x02(\r\x12\x10\n\x08vchannel\x18\x02 \x01(\r\"\x9f\x01\n\x1ftune_param_channels_conf_record\x12\x0f\n\x07version\x18\x01 \x02(\r\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x11\n\tfrequency\x18\x03 \x01(\r\x12\x12\n\nmodulation\x18\x04 \x01(\t\x12\x10\n\x08video_id\x18\x05 \x01(\r\x12\x10\n\x08\x61udio_id\x18\x06 \x01(\r\x12\x12\n\nprogram_id\x18\x07 \x01(\r\"\xfd\x01\n\x04tune\x12\x0f\n\x07version\x18\x01 \x02(\r\x12\x37\n\x0eparameter_type\x18\x02 \x01(\x0e\x32\x1f.tvserver.tune.parameter_type_e\x12/\n\x08vchannel\x18\x03 \x01(\x0b\x32\x1d.tvserver.tune_param_vchannel\x12\x46\n\x13\x63hannelsconf_record\x18\x04 \x01(\x0b\x32).tvserver.tune_param_channels_conf_record\"2\n\x10parameter_type_e\x12\x0c\n\x08VCHANNEL\x10\x00\x12\x10\n\x0c\x43HANNELSCONF\x10\x01\"B\n\rtune_response\x12\x0f\n\x07version\x18\x01 \x02(\r\x12\x0f\n\x07success\x18\x02 \x01(\x08\x12\x0f\n\x07message\x18\x03 \x01(\t')



_TUNE_PARAMETER_TYPE_E = descriptor.EnumDescriptor(
  name='parameter_type_e',
  full_name='tvserver.tune.parameter_type_e',
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
  serialized_start=448,
  serialized_end=498,
)


_TUNE_PARAM_VCHANNEL = descriptor.Descriptor(
  name='tune_param_vchannel',
  full_name='tvserver.tune_param_vchannel',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='version', full_name='tvserver.tune_param_vchannel.version', index=0,
      number=1, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='vchannel', full_name='tvserver.tune_param_vchannel.vchannel', index=1,
      number=2, type=13, cpp_type=3, label=1,
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
  serialized_start=24,
  serialized_end=80,
)


_TUNE_PARAM_CHANNELS_CONF_RECORD = descriptor.Descriptor(
  name='tune_param_channels_conf_record',
  full_name='tvserver.tune_param_channels_conf_record',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='version', full_name='tvserver.tune_param_channels_conf_record.version', index=0,
      number=1, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='name', full_name='tvserver.tune_param_channels_conf_record.name', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='frequency', full_name='tvserver.tune_param_channels_conf_record.frequency', index=2,
      number=3, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='modulation', full_name='tvserver.tune_param_channels_conf_record.modulation', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='video_id', full_name='tvserver.tune_param_channels_conf_record.video_id', index=4,
      number=5, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='audio_id', full_name='tvserver.tune_param_channels_conf_record.audio_id', index=5,
      number=6, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='program_id', full_name='tvserver.tune_param_channels_conf_record.program_id', index=6,
      number=7, type=13, cpp_type=3, label=1,
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
  serialized_start=83,
  serialized_end=242,
)


_TUNE = descriptor.Descriptor(
  name='tune',
  full_name='tvserver.tune',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='version', full_name='tvserver.tune.version', index=0,
      number=1, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='parameter_type', full_name='tvserver.tune.parameter_type', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='vchannel', full_name='tvserver.tune.vchannel', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='channelsconf_record', full_name='tvserver.tune.channelsconf_record', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _TUNE_PARAMETER_TYPE_E,
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=245,
  serialized_end=498,
)


_TUNE_RESPONSE = descriptor.Descriptor(
  name='tune_response',
  full_name='tvserver.tune_response',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='version', full_name='tvserver.tune_response.version', index=0,
      number=1, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='success', full_name='tvserver.tune_response.success', index=1,
      number=2, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='message', full_name='tvserver.tune_response.message', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
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
  serialized_start=500,
  serialized_end=566,
)

_TUNE.fields_by_name['parameter_type'].enum_type = _TUNE_PARAMETER_TYPE_E
_TUNE.fields_by_name['vchannel'].message_type = _TUNE_PARAM_VCHANNEL
_TUNE.fields_by_name['channelsconf_record'].message_type = _TUNE_PARAM_CHANNELS_CONF_RECORD
_TUNE_PARAMETER_TYPE_E.containing_type = _TUNE;
DESCRIPTOR.message_types_by_name['tune_param_vchannel'] = _TUNE_PARAM_VCHANNEL
DESCRIPTOR.message_types_by_name['tune_param_channels_conf_record'] = _TUNE_PARAM_CHANNELS_CONF_RECORD
DESCRIPTOR.message_types_by_name['tune'] = _TUNE
DESCRIPTOR.message_types_by_name['tune_response'] = _TUNE_RESPONSE

class tune_param_vchannel(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _TUNE_PARAM_VCHANNEL
  
  # @@protoc_insertion_point(class_scope:tvserver.tune_param_vchannel)

class tune_param_channels_conf_record(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _TUNE_PARAM_CHANNELS_CONF_RECORD
  
  # @@protoc_insertion_point(class_scope:tvserver.tune_param_channels_conf_record)

class tune(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _TUNE
  
  # @@protoc_insertion_point(class_scope:tvserver.tune)

class tune_response(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _TUNE_RESPONSE
  
  # @@protoc_insertion_point(class_scope:tvserver.tune_response)

# @@protoc_insertion_point(module_scope)
