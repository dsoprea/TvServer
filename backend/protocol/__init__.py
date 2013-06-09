from backend.protocol.tune_pb2 import tune, tune_response

MT_TUNE = 'tune'
MT_TUNE_RESPONSE = 'tune_response'

_message_list = ((MT_TUNE, tune),
                 (MT_TUNE_RESPONSE, tune_response))

_messages_bytype = {}
_messages_byindex = {}

i = 0
for (constant, cls) in _message_list:
    _messages_bytype[constant] = (i, cls)
    _messages_byindex[i] = (constant, cls)
    
    i += 1

def get_message_index_by_cls(cls):
    return _messages_bytype[cls.__name__][0]

def get_message_cls_by_index(index):
    return _messages_byindex[index][1]
    