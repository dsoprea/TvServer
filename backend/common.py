import os

from struct import pack

from backend.protocol import get_message_index_by_cls

def serialize_message(message):
    message_index = get_message_index_by_cls(message.__class__)
    
    flat = message.SerializeToString()

    marker = os.urandom(4)
    header = pack('>II', len(flat), message_index)
    raw_message = header + marker + flat + marker

    return raw_message