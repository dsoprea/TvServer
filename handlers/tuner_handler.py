import logging

from interfaces.device.itunerdriver import TD_TYPE_CHANNELSCONF, \
                                           TD_TYPE_VCHANNEL

import values

from cf import get
from handlers import GetHandler
from device.drivers import get_big_id_from_device
from device.tuner_info import TunerInfo
from device import NoTunersAvailable, TunerNotAllocated
from handlers import RequestError
from backend.protocol.tune_pb2 import tune
from backend.protocol.cleartune_pb2 import cleartune
from backend.protocol.acquire_pb2 import acquire
from backend.protocol.devicestatus_pb2 import devicestatus
from backend.client import Client

class TunerHandler(GetHandler):
    def __init__(self):
        super(TunerHandler, self).__init__()
        self.__client = Client()
    
    def acquire(self, bdid):
        """Acquire exclusive access to a tuner, prior to tuning.
        
        bdid: Device BigID.
        """

        try:
            acquire_msg = acquire()
            acquire_msg.version = 1
            acquire_msg.device_bigid = bdid

            response = self.__client.send_query(acquire_msg)
            
            if response.success == False:
                raise RequestError("Acquire failed: %s" % (response.message))
            
            return { 'tid': response.tuning_bigid }
        except NoTunersAvailable:
            raise
        except RequestError:
            raise
        except:
            message = ("There was an error while tuning on [%s]." % (bdid))

            logging.exception(message)
            raise Exception(message)

    def tunevc(self, tid, vc):
        """Tune a channel on a device requiring a single virtual-channel."""

        try:
            tuner = TunerInfo.build_from_id(tid)
            
            if tuner.is_allocated() is False:
                raise TunerNotAllocated("Tuner is either not valid or not "
                                        "allocated.")
            
            driver = tuner.device.driver
            if driver.tuner.data_type != TD_TYPE_VCHANNEL:
                raise Exception("This interface requires virtual-channel "
                                "parameters.")

            #tuner.tune(tuner, vc)
        except TunerNotAllocated:
            raise
        except RequestError:
            raise
        except:
            message = "Error while trying to tune (VC)."
            
            logging.exception(message)
            raise Exception(message)

    def tunecc(self, tid, name, freq, mod, vid, aid, pid):
        """Tune a channel on a device requiring channels-conf data."""

        try:
            tuner = TunerInfo.build_from_id(tid)
            
            driver = tuner.device.driver
            if driver.tuner_data_type != TD_TYPE_CHANNELSCONF:
                raise Exception("This interface required channels-conf "
                                "parameters.")
                
            tune_msg = tune()
            tune_msg.version = 1
            tune_msg.tuning_bigid = tid
            tune_msg.parameter_type = tune.CHANNELSCONF
            tune_msg.channelsconf_record.version = 1
            tune_msg.channelsconf_record.name = name;
            tune_msg.channelsconf_record.frequency = int(freq);
            tune_msg.channelsconf_record.modulation = mod;
            tune_msg.channelsconf_record.video_id = int(vid);
            tune_msg.channelsconf_record.audio_id = int(aid);
            tune_msg.channelsconf_record.program_id = int(pid);
# TODO: the web request handler should only receive responses addressed to that particular thread.
            # Expect a general_response in responsee.
            response = self.__client.send_query(tune_msg)
            
            if response.success == False:
                raise Exception("Tune failed: %s" % (response.message))
            
            return { "Success": True }
        except:
            message = "Error while trying to tune."
            
            logging.exception(message)
            raise Exception(message)

    def cleartune(self, tid):
        """Stop tuning."""

        try:
            cleartune_msg = cleartune()
            cleartune_msg.version = 1
            cleartune_msg.tuning_bigid = tid
            
            # Expect a general_response in responsee.
            response = self.__client.send_query(cleartune_msg)
            
            if response.success == False:
                raise Exception("Clear-tune failed: %s" % (response.message))
            
            return { "Success": True }
        except:
            message = "Error while trying to clear the tune."
            
            logging.exception(message)
            raise Exception(message)

    def status(self):
        try:
            devicestatus_msg = devicestatus()
            devicestatus_msg.version = 1

            response_msg = self.__client.send_query(devicestatus_msg)

            response = {}
            for driver_msg in response_msg.drivers:
                devices = {}
                for device_msg in driver_msg.devices:
                    tuner_ids = []
                    for tuner_id in device_msg.tuner_ids:
                        tuner_ids.append(tuner_id)

                    devices[device_msg.bdid] = tuner_ids

                response[driver_msg.dcn] = devices
    
            return response
        except:
            message = "Error while requesting tuning statuses."

            logging.exception(message)
            raise Exception(message)
