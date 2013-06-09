import logging

from interfaces.device.itunerdriver import TD_TYPE_CHANNELSCONF, \
                                           TD_TYPE_VCHANNEL

import values

from cf import get
from handlers import GetHandler
from device.drivers import available_drivers, get_device_from_big_id, \
                           get_big_id_from_device
from device.tuner import Tuner
from device.tuner_info import TunerInfo
from device import NoTunersAvailable, TunerNotAllocated
from device.channels.channelsconf_record import ChannelsConfRecord
from big_id import BigId
from handlers import RequestError
from backend.protocol.tune_pb2 import tune
from backend.client import Client

class TunerHandler(GetHandler):
    def acquire(self, bdid):
        """Acquire exclusive access to a tuner, prior to tuning.
        
        bdid: Device BigID.
        """

        try:
            tuner = get(values.C_DEV_TUNER)
            
            device = get_device_from_big_id(BigId(bdid))
    
            tuner = tuner.request_tuner(specific_device=device)
            if tuner is None:
                raise NoTunersAvailable("No tuners are available on device "
                                        "[%s]." % (bdid))
            
            return { 'tid': tuner.identifier }
        except NoTunersAvailable:
            raise
        except RequestError:
            raise
        except:
            message = ("There was an error while tuning on [%s]." % (bdid))

            logging.exception(message)
            raise Exception(message)

    def tunevc(self, tid, vc):
        """Tune a channel using a single virtual-channel."""

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
        """Tune a channel.

        Arguments depend on the tuning requirements of the driver.
        """

        try:
            tuner = TunerInfo.build_from_id(tid)

            if tuner.is_allocated() is False:
                raise TunerNotAllocated("Tuner is either not valid or not "
                                        "allocated.")
            
            driver = tuner.device.driver
            if driver.tuner_data_type != TD_TYPE_CHANNELSCONF:
                raise Exception("This interface required channels-conf "
                                "parameters.")
                
            tune_msg = tune()
            tune_msg.version = 1
            tune_msg.parameter_type = tune.CHANNELSCONF
            tune_msg.channelsconf_record.version = 1
            tune_msg.channelsconf_record.name = name;
            tune_msg.channelsconf_record.frequency = int(freq);
            tune_msg.channelsconf_record.modulation = mod;
            tune_msg.channelsconf_record.video_id = int(vid);
            tune_msg.channelsconf_record.audio_id = int(aid);
            tune_msg.channelsconf_record.program_id = int(pid);
            
            # Expect a tune_response in responsee.
            response = Client().send_query(tune_msg)
            
            if response.success == False:
                raise Exception("Tune failed: %s" % (response.message))
            
            return { "Success": True }
            
        except TunerNotAllocated:
            raise
        except RequestError:
            raise
        except:
            message = "Error while trying to tune."
            
            logging.exception(message)
            raise Exception(message)

    def status(self):
        try:
            tuner = get(values.C_DEV_TUNER)
            
            response = {}
            for tuner in tuner.get_statuses().keys():
                device = tuner.device
                driver = device.driver
                
                driver_class_name = driver.__class__.__name__
                if driver_class_name not in response:
                    response[driver_class_name] = {}
                
                device_big_id_str = repr(get_big_id_from_device(device))
                tuner_id = tuner.identifier
    
                if device_big_id_str not in response[driver_class_name]:
                    response[driver_class_name][device_big_id_str] = [tuner_id]
                else:
                    response[driver_class_name][device_big_id_str].append(tuner_id)
    
            return response
        except RequestError:
            raise
        except:
            message = "Error while trying to find tuning statuses."

            logging.exception(message)
            raise Exception(message)
