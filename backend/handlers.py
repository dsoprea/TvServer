import values

from cf import get
from device.drivers import get_device_from_big_id
from big_id import BigId
from backend.protocol.acquire_pb2 import acquireresponse
from backend.protocol.tune_pb2 import tune
from backend.protocol.general_pb2 import generalresponse
from device.tuner_info import TunerInfo
from interfaces.device.itunerdriver import TD_TYPE_CHANNELSCONF, \
                                           TD_TYPE_VCHANNEL
from device.channels.channelsconf_record import ChannelsConfRecord

class Handlers(object):
    def __init__(self):
        self.__tuner = get(values.C_DEV_TUNER)
    
    def handleAcquire(self, message):
        bdid = message.device_bigid
        
        device = get_device_from_big_id(BigId(bdid))
        tuner = self.__tuner.request_tuner(specific_device=device)

        response = acquireresponse()
        response.version = 1

        if tuner is None:
            response.success = False
            response.error_type = 'tuner'
            response.message = ("No tuners are available on device "
                                "[%s]." % (bdid))
        else:
            response.success = True
            response.tuning_bigid = tuner.identifier

        return response

    def handleCleartune(self, message):
        btid = message.tuning_bigid

        tuner = TunerInfo.build_from_id(btid)
        tuner.tune(None)

        response = generalresponse()
        response.version = 1
        response.success = True
        
        return response

    def handleTune(self, message):
        btid = message.tuning_bigid

        tuner = TunerInfo.build_from_id(btid)
        driver = tuner.device.driver

        response = generalresponse()
        response.version = 1
        response.success = False
        
        if tuner.is_allocated() is False:
            response.error_type = 'tuner'
            response.message = ("Tuner [%s] is either not valid or not "
                                "allocated." % (btid))

            return response
        
        if message.parameter_type == tune.VCHANNEL:
            if driver.tuner_data_type != TD_TYPE_VCHANNEL:
                response.error_type = 'arguments'
                response.message = ("Received channels.conf data instead of "
                                    "vchannel data.")
    
                return response

            response.success = True
# TODO: Finish.
            #tuner.tune(message.vchannel.vchannel)
        elif message.parameter_type == tune.CHANNELSCONF:
            if driver.tuner_data_type != TD_TYPE_CHANNELSCONF:
                response.error_type = 'arguments'
                response.message = ("Received vchannel data instead of "
                                    "channels.conf data.")
    
                return response

            msg_cc = message.channelsconf_record
            cc_record = ChannelsConfRecord(name=msg_cc.name,
                                           freq=msg_cc.frequency,
                                           mod=msg_cc.modulation,
                                           vid=msg_cc.video_id,
                                           aid=msg_cc.audio_id,
                                           pid=msg_cc.program_id)
                               
            response.success = True
            tuner.tune(cc_record)
        else:
            response.error_type = 'arguments'
            response.message = ("Received unexpected data of type [%s] instead"
                                "of relevant tuning data." % 
                                (message.__class__.__name__))

        return response
