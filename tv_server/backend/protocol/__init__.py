from tv_server.backend.protocol.tuner_tune_pb2 import tuner_tune
from tv_server.backend.protocol.tuner_acquire_pb2 import tuner_acquire, \
                                                         tuner_acquireresponse
from tv_server.backend.protocol.tuner_clear_pb2 import tuner_clear
from tv_server.backend.protocol.tuner_status_pb2 import tuner_status, \
                                                        tuner_statusresponse
from tv_server.backend.protocol.device_list_pb2 import device_list, \
                                                       device_listresponse
from tv_server.backend.protocol.driver_list_pb2 import driver_list, \
                                                       driver_listresponse
from tv_server.backend.protocol.driver_info_pb2 import driver_info, \
                                                       driver_inforesponse
from tv_server.backend.protocol.error_pb2 import error
from tv_server.backend.protocol.general_pb2 import generalresponse

MT_GENERALRESPONSE = 'generalresponse'
MT_ERROR = 'error'
MT_TUNER_ACQUIRE = 'tuner_acquire'
MT_TUNER_ACQUIRERESPONSE = 'tuner_acquireresponse'
MT_TUNER_CLEAR = 'tuner_clear'
MT_TUNER_TUNE = 'tuner_tune'
MT_TUNER_STATUS = 'tuner_status'
MT_TUNER_STATUSRESPONSE = 'tuner_statusresponse'
MT_DEVICE_LIST = 'device_list'
MT_DEVICE_LISTRESPONSE = 'device_listresponse'
MT_DRIVER_LIST = 'driver_list'
MT_DRIVER_LISTRESPONSE = 'driver_listresponse'
MT_DRIVER_INFO = 'driver_info'
MT_DRIVER_INFORESPONSE = 'driver_inforesponse'

_message_list = ((MT_GENERALRESPONSE, generalresponse),
                 (MT_TUNER_TUNE, tuner_tune),
                 (MT_TUNER_ACQUIRE, tuner_acquire),
                 (MT_TUNER_ACQUIRERESPONSE, tuner_acquireresponse),
                 (MT_TUNER_CLEAR, tuner_clear),
                 (MT_TUNER_STATUS, tuner_status),
                 (MT_TUNER_STATUSRESPONSE, tuner_statusresponse),
                 (MT_DEVICE_LIST, device_list),
                 (MT_DEVICE_LISTRESPONSE, device_listresponse),
                 (MT_DRIVER_LIST, driver_list),
                 (MT_DRIVER_LISTRESPONSE, driver_listresponse),
                 (MT_DRIVER_INFO, driver_info),
                 (MT_DRIVER_INFORESPONSE, driver_inforesponse),
                 (MT_ERROR, error))

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
    