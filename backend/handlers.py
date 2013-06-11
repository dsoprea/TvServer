import values

from cf import get
from device.drivers import get_device_from_big_id, get_big_id_from_device
from big_id import BigId
from backend.protocol.acquire_pb2 import acquireresponse
from backend.protocol.tune_pb2 import tune
from backend.protocol.general_pb2 import generalresponse
from backend.protocol.devicestatus_pb2 import devicestatusresponse
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

    def handleDevicestatus(self, message):
        tuner = get(values.C_DEV_TUNER)

        response = {}
        for device, tuner_info_list in tuner.get_statuses().iteritems():
            driver = device.driver
            dcn = driver.__class__.__name__
            if dcn not in response:
                response[dcn] = {}
            
            device_big_id_str = repr(get_big_id_from_device(device))

            for tuner_info in tuner_info_list:
                if device_big_id_str not in response[dcn]:
                    response[dcn][device_big_id_str] = [tuner_info.identifier]
                else:
                    response[dcn][device_big_id_str].append(tuner_info.identifier)

        response_msg = devicestatusresponse()
        response_msg.version = 1

        for dcn, devices in response.iteritems():
            driver = response_msg.drivers.add()
            driver.version = 1
            driver.dcn = dcn
            
            for bdid_str, tuners in devices.iteritems():
                device = driver.devices.add()
                device.version = 1
                device.bdid = bdid_str
                
                for tuner_id in tuners:
                    device.tuner_ids.append(tuner_id)
            
        return response_msg
