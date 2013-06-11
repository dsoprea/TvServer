from backend.protocol.tune_pb2 import tune
from backend.protocol.acquire_pb2 import acquire, acquireresponse
from backend.protocol.error_pb2 import error
from backend.protocol.cleartune_pb2 import cleartune
from backend.protocol.general_pb2 import generalresponse
from backend.protocol.devicestatus_pb2 import devicestatus, \
                                              devicestatusresponse

MT_TUNE = 'tune'
MT_GENERALRESPONSE = 'generalresponse'
MT_ACQUIRE = 'acquire'
MT_ACQUIRERESPONSE = 'acquireresponse'
MT_CLEARTUNE = 'cleartune'
MT_DEVICESTATUS = 'devicestatus'
MT_DEVICESTATUSRESPONSE = 'devicestatusresponse'

_message_list = ((MT_GENERALRESPONSE, generalresponse),
                 (MT_TUNE, tune),
                 (MT_ACQUIRE, acquire),
                 (MT_ACQUIRERESPONSE, acquireresponse),
                 (MT_CLEARTUNE, cleartune),
                 (MT_DEVICESTATUS, devicestatus),
                 (MT_DEVICESTATUSRESPONSE, devicestatusresponse))

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
    