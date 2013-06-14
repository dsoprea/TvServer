from tv_server import values

from tv_server.cf import get
from tv_server.device.drivers import get_device_from_big_id, \
                                     get_big_id_from_device, \
                                     available_drivers
from tv_server.big_id import BigId
from tv_server.backend.protocol.acquire_pb2 import acquireresponse
from tv_server.backend.protocol.tune_pb2 import tune
from tv_server.backend.protocol.general_pb2 import generalresponse
from tv_server.backend.protocol.devicestatus_pb2 import devicestatusresponse
from tv_server.backend.protocol.devicelist_pb2 import devicelistresponse
from tv_server.backend.protocol.driverlist_pb2 import driverlistresponse
from tv_server.backend.protocol.driverinfo_pb2 import driverinforesponse
from tv_server.device.tuner_info import TunerInfo
from tv_server.interfaces.device.itunerdriver import TD_TYPE_CHANNELSCONF, \
                                                     TD_TYPE_VCHANNEL
from tv_server.device.channels.channelsconf_record import ChannelsConfRecord


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
        self.__tuner.release_tuner(tuner)

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
        
        target = (message.target.host, message.target.port)

        if message.parameter_type == tune.VCHANNEL:
            if driver.tuner_data_type != TD_TYPE_VCHANNEL:
                response.error_type = 'arguments'
                response.message = ("Received channels.conf data instead of "
                                    "vchannel data.")
    
                return response

            tuner.set_tune(message.vchannel.vchannel, target)

            response.success = True
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

            tuner.set_tune(cc_record, target)

            response.success = True
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
        response_msg.success = True

        for dcn, devices in response.iteritems():
            driver = response_msg.drivers.add()
            driver.dcn = dcn
            
            for bdid_str, tuners in devices.iteritems():
                device = driver.devices.add()
                device.bdid = bdid_str
                
                for tuner_id in tuners:
                    device.tuner_ids.append(tuner_id)
            
        return response_msg

    def handleDevicelist(self, message):
        """Find devices for the given driver.

        dcn: Driver class name
        """

        (driver_cls, device_cls) = available_drivers[message.dcn]
        devices_raw = driver_cls().enumerate_devices()

        response = devicelistresponse()
        response.version = 1
        response.success = True

        for device in devices_raw:
            device_msg = response.devices.add() 
            device_msg.bdid = repr(get_big_id_from_device(device))
            device_msg.address = device.address
            device_msg.tuner_quantity = device.tuner_quantity

        return response

    def handleDriverlist(self, message):
        response = driverlistresponse()
        response.version = 1
        response.success = True

        for pair in available_drivers.iteritems():
            (driver_cls_name, (driver_cls, device_cls)) = pair
            driver = driver_cls()

            driver_msg = response.drivers.add()
            driver_msg.dcn = driver_cls_name
            driver_msg.name = driver.name
            driver_msg.description = driver.description

        return response

    def handleDriverinfo(self, message):
        (driver_cls, device_cls) = available_drivers[message.dcn]
        driver = driver_cls()
        
        response = driverinforesponse()
        response.version = 1
        response.success = True
        response.tune_type = driver.tuner_data_type
        response.stream_mimetype = driver.stream_mimetype  
        
        return response
