import os

from struct import pack
from threading import current_thread

from backend.protocol import get_message_index_by_cls


class ResponseTimeout(Exception):
    pass

def serialize_message(message, to_thread_id=0):
    message_index = get_message_index_by_cls(message.__class__)
    
    flat = message.SerializeToString()

    marker = os.urandom(4)
    thread_id = current_thread().ident
    
    # We don't pack the marker because it doesn't matter. It's four bytes and
    # will be added to both sides. As long as the two are equal when received, 
    # we're good.
    header = pack('>IQQI', len(flat), 
                           thread_id, 
                           to_thread_id, 
                           message_index)

    raw_message = header + marker + flat + marker

    return raw_message
