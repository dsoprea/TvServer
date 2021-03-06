from tv_server.interfaces.device.itunerdriver import TD_TYPE_CHANNELSCONF, \
                                                     TD_TYPE_VCHANNEL
from tv_server.handlers import GetHandler
from tv_server.device.tuner_info import TunerInfo
from tv_server.handlers import RequestError
from tv_server.backend.protocol.tuner_tune_pb2 import tuner_tune
from tv_server.backend.protocol.tuner_clear_pb2 import tuner_clear
from tv_server.backend.protocol.tuner_acquire_pb2 import tuner_acquire
from tv_server.backend.protocol.tuner_status_pb2 import tuner_status
from tv_server.backend.protocol.error_pb2 import error
from tv_server.backend.client import Client


class TunerHandler(GetHandler):
    def __init__(self):
        super(TunerHandler, self).__init__()
        self.__client = Client()
    
    def acquire(self, bdid):
        """Acquire exclusive access to a tuner, prior to tuning.
        
        bdid: Device BigID.
        """

        acquire_msg = tuner_acquire()
        acquire_msg.version = 1
        acquire_msg.device_bigid = bdid

        response = self.__client.send_query(acquire_msg)
        if response.__class__ == error or response.success == False:
            raise RequestError("Acquire failed: %s" % (response.message))
        
        return { 'btid': response.tuning_bigid }

    def tunevc(self, btid, thost, tport, vc):
        """Tune a channel on a device requiring a single virtual-channel."""

        tuner = TunerInfo.build_from_id(btid)
        
        driver = tuner.device.driver
        if driver.tuner_data_type != TD_TYPE_VCHANNEL:
            raise RequestError("This interface requires virtual-channel "
                               "parameters.")

        tune_msg = tuner_tune()
        tune_msg.version = 1
        tune_msg.tuning_bigid = btid
        tune_msg.parameter_type = tuner_tune.VCHANNEL
        tune_msg.vchannel.vchannel = int(vc);
        tune_msg.target.host = thost
        tune_msg.target.port = int(tport)

        # Expect a general_response in responsee.
        response = self.__client.send_query(tune_msg)
        if response.__class__ == error or response.success == False:
            raise RequestError("Tune failed: %s" % (response.message))
        
        return { "Success": True }

    def tuneccshort(self, btid, cc, thost='127.0.0.1', tport=5000):
        """Tune a channel on a device requiring channels-conf data."""

        tuner = TunerInfo.build_from_id(btid)
        
        driver = tuner.device.driver
        if driver.tuner_data_type != TD_TYPE_CHANNELSCONF:
            raise RequestError("This interface required channels-conf "
                               "parameters.")
            
        cc_parts = cc.split(':')
        
        if len(cc_parts) < 6:
            raise RequestError("The CC string should have six colon-separated "
                               "parts.")
        
        (name, freq, mod, vid, aid, sid) = cc_parts 
            
        tune_msg = tuner_tune()
        tune_msg.version = 1
        tune_msg.tuning_bigid = btid
        tune_msg.parameter_type = tuner_tune.CHANNELSCONF
        tune_msg.channelsconf_record.name = name;
        tune_msg.channelsconf_record.frequency = int(freq);
        tune_msg.channelsconf_record.modulation = mod;
        tune_msg.channelsconf_record.video_id = int(vid);
        tune_msg.channelsconf_record.audio_id = int(aid);
        tune_msg.channelsconf_record.stream_id = int(sid);
        tune_msg.target.host = thost
        tune_msg.target.port = int(tport)

        # Expect a general_response in responsee.
        response = self.__client.send_query(tune_msg)
        if response.__class__ == error or response.success == False:
            raise RequestError("Tune failed: %s" % (response.message))
        
        return { "Success": True }

    def tunecclong(self, btid, thost, tport, name, freq, mod, vid, aid, pid):
        """Tune a channel on a device requiring channels-conf data."""

        tuner = TunerInfo.build_from_id(btid)
        
        driver = tuner.device.driver
        if driver.tuner_data_type != TD_TYPE_CHANNELSCONF:
            raise RequestError("This interface required channels-conf "
                               "parameters.")
            
        tune_msg = tuner_tune()
        tune_msg.version = 1
        tune_msg.tuning_bigid = btid
        tune_msg.parameter_type = tuner_tune.CHANNELSCONF
        tune_msg.channelsconf_record.name = name;
        tune_msg.channelsconf_record.frequency = int(freq);
        tune_msg.channelsconf_record.modulation = mod;
        tune_msg.channelsconf_record.video_id = int(vid);
        tune_msg.channelsconf_record.audio_id = int(aid);
        tune_msg.channelsconf_record.program_id = int(pid);
        tune_msg.target.host = thost
        tune_msg.target.port = int(tport)

        # Expect a general_response in responsee.
        response = self.__client.send_query(tune_msg)
        
        if response.__class__ == error or response.success == False:
            raise RequestError("Tune failed: %s" % (response.message))
        
        return { "Success": True }

    def release(self, btid):
        """Stop tuning."""

        tuneclear_msg = tuner_clear()
        tuneclear_msg.version = 1
        tuneclear_msg.tuning_bigid = btid
        
        # Expect a general_response in responsee.
        response = self.__client.send_query(tuneclear_msg)
        if response.__class__ == error or response.success == False:
            raise RequestError("Tune-clear failed: %s" % (response.message))
        
        return { "Success": True }

    def status(self):
        tunerstatus_msg = tuner_status()
        tunerstatus_msg.version = 1

        response = self.__client.send_query(tunerstatus_msg)
        if response.__class__ == error or response.success == False:
            raise RequestError("Tune-status failed: %s" % (response.message))

        drivers = {}
        for driver_msg in response.drivers:
            devices = {}
            for device_msg in driver_msg.devices:
                tuner_ids = []
                for tuner_id in device_msg.tuner_ids:
                    tuner_ids.append(tuner_id)

                devices[device_msg.bdid] = tuner_ids

            drivers[driver_msg.dcn] = devices

        return drivers
