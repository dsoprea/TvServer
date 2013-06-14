from tv_server.backend.protocol.tune_pb2 import tune
from tv_server.backend.protocol.acquire_pb2 import acquire, acquireresponse
from tv_server.backend.protocol.error_pb2 import error
from tv_server.backend.protocol.cleartune_pb2 import cleartune
from tv_server.backend.protocol.general_pb2 import generalresponse
from tv_server.backend.protocol.devicestatus_pb2 import devicestatus, \
                                                        devicestatusresponse
from tv_server.backend.protocol.devicelist_pb2 import devicelist, \
                                                      devicelistresponse
from tv_server.backend.protocol.driverlist_pb2 import driverlist, \
                                                      driverlistresponse
from tv_server.backend.protocol.driverinfo_pb2 import driverinfo, \
                                                      driverinforesponse

MT_TUNE = 'tune'
MT_GENERALRESPONSE = 'generalresponse'
MT_ACQUIRE = 'acquire'
MT_ACQUIRERESPONSE = 'acquireresponse'
MT_CLEARTUNE = 'cleartune'
MT_DEVICESTATUS = 'devicestatus'
MT_DEVICESTATUSRESPONSE = 'devicestatusresponse'
MT_DEVICELIST = 'devicelist'
MT_DEVICELISTRESPONSE = 'devicelistresponse'
MT_DRIVERLIST = 'driverlist'
MT_DRIVERLISTRESPONSE = 'driverlistresponse'
MT_DRIVERINFO = 'driverinfo'
MT_DRIVERINFORESPONSE = 'driverinforesponse'

_message_list = ((MT_GENERALRESPONSE, generalresponse),
                 (MT_TUNE, tune),
                 (MT_ACQUIRE, acquire),
                 (MT_ACQUIRERESPONSE, acquireresponse),
                 (MT_CLEARTUNE, cleartune),
                 (MT_DEVICESTATUS, devicestatus),
                 (MT_DEVICESTATUSRESPONSE, devicestatusresponse),
                 (MT_DEVICELIST, devicelist),
                 (MT_DEVICELISTRESPONSE, devicelistresponse),
                 (MT_DRIVERLIST, driverlist),
                 (MT_DRIVERLISTRESPONSE, driverlistresponse),
                 (MT_DRIVERINFO, driverinfo),
                 (MT_DRIVERINFORESPONSE, driverinforesponse))

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
    