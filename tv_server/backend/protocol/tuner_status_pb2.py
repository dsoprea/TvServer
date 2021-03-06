# Generated by the protocol buffer compiler.  DO NOT EDIT!

from google.protobuf import descriptor
from google.protobuf import message
from google.protobuf import reflection
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)



DESCRIPTOR = descriptor.FileDescriptor(
  name='tuner_status.proto',
  package='tvserver',
  serialized_pb='\n\x12tuner_status.proto\x12\x08tvserver\"\x1f\n\x0ctuner_status\x12\x0f\n\x07version\x18\x01 \x02(\r\"\xea\x01\n\x14tuner_statusresponse\x12\x0f\n\x07version\x18\x01 \x02(\r\x12\x0f\n\x07success\x18\x02 \x01(\x08\x12\x36\n\x07\x64rivers\x18\x03 \x03(\x0b\x32%.tvserver.tuner_statusresponse.driver\x1a)\n\x06\x64\x65vice\x12\x0c\n\x04\x62\x64id\x18\x01 \x01(\t\x12\x11\n\ttuner_ids\x18\x02 \x03(\t\x1aM\n\x06\x64river\x12\x0b\n\x03\x64\x63n\x18\x01 \x01(\t\x12\x36\n\x07\x64\x65vices\x18\x02 \x03(\x0b\x32%.tvserver.tuner_statusresponse.device')




_TUNER_STATUS = descriptor.Descriptor(
  name='tuner_status',
  full_name='tvserver.tuner_status',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='version', full_name='tvserver.tuner_status.version', index=0,
      number=1, type=13, cpp_type=3, label=2,
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
  serialized_start=32,
  serialized_end=63,
)


_TUNER_STATUSRESPONSE_DEVICE = descriptor.Descriptor(
  name='device',
  full_name='tvserver.tuner_statusresponse.device',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='bdid', full_name='tvserver.tuner_statusresponse.device.bdid', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='tuner_ids', full_name='tvserver.tuner_statusresponse.device.tuner_ids', index=1,
      number=2, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
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
  serialized_start=180,
  serialized_end=221,
)

_TUNER_STATUSRESPONSE_DRIVER = descriptor.Descriptor(
  name='driver',
  full_name='tvserver.tuner_statusresponse.driver',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='dcn', full_name='tvserver.tuner_statusresponse.driver.dcn', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=unicode("", "utf-8"),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='devices', full_name='tvserver.tuner_statusresponse.driver.devices', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
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
  serialized_start=223,
  serialized_end=300,
)

_TUNER_STATUSRESPONSE = descriptor.Descriptor(
  name='tuner_statusresponse',
  full_name='tvserver.tuner_statusresponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    descriptor.FieldDescriptor(
      name='version', full_name='tvserver.tuner_statusresponse.version', index=0,
      number=1, type=13, cpp_type=3, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='success', full_name='tvserver.tuner_statusresponse.success', index=1,
      number=2, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    descriptor.FieldDescriptor(
      name='drivers', full_name='tvserver.tuner_statusresponse.drivers', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_TUNER_STATUSRESPONSE_DEVICE, _TUNER_STATUSRESPONSE_DRIVER, ],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  serialized_start=66,
  serialized_end=300,
)

_TUNER_STATUSRESPONSE_DEVICE.containing_type = _TUNER_STATUSRESPONSE;
_TUNER_STATUSRESPONSE_DRIVER.fields_by_name['devices'].message_type = _TUNER_STATUSRESPONSE_DEVICE
_TUNER_STATUSRESPONSE_DRIVER.containing_type = _TUNER_STATUSRESPONSE;
_TUNER_STATUSRESPONSE.fields_by_name['drivers'].message_type = _TUNER_STATUSRESPONSE_DRIVER
DESCRIPTOR.message_types_by_name['tuner_status'] = _TUNER_STATUS
DESCRIPTOR.message_types_by_name['tuner_statusresponse'] = _TUNER_STATUSRESPONSE

class tuner_status(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  DESCRIPTOR = _TUNER_STATUS
  
  # @@protoc_insertion_point(class_scope:tvserver.tuner_status)

class tuner_statusresponse(message.Message):
  __metaclass__ = reflection.GeneratedProtocolMessageType
  
  class device(message.Message):
    __metaclass__ = reflection.GeneratedProtocolMessageType
    DESCRIPTOR = _TUNER_STATUSRESPONSE_DEVICE
    
    # @@protoc_insertion_point(class_scope:tvserver.tuner_statusresponse.device)
  
  class driver(message.Message):
    __metaclass__ = reflection.GeneratedProtocolMessageType
    DESCRIPTOR = _TUNER_STATUSRESPONSE_DRIVER
    
    # @@protoc_insertion_point(class_scope:tvserver.tuner_statusresponse.driver)
  DESCRIPTOR = _TUNER_STATUSRESPONSE
  
  # @@protoc_insertion_point(class_scope:tvserver.tuner_statusresponse)

# @@protoc_insertion_point(module_scope)
