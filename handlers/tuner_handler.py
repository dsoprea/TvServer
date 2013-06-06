import logging

from handlers import GetHandler
from device.drivers import available_drivers, get_device_from_big_id, \
                           get_big_id_from_device
from device.tuner import Tuner
from device.tuner_info import TunerInfo
from device import NoTunersAvailable
from big_id import BigId

_tuner = Tuner()


class TunerHandler(GetHandler):
    def acquire(self, bdid):
        """Acquire exclusive access to a tuner, prior to tuning.
        
        bdid: Device BigID.
        """

        try:
            device = get_device_from_big_id(BigId(bdid))
    
            tuner = _tuner.request_tuner(specific_device=device)
            if tuner is None:
                raise NoTunersAvailable("No tuners are available on device "
                                        "[%s]." % (bdid))
            
            return { 'tid': tuner.identifier }
        except NoTunersAvailable:
            raise
        except:
            message = ("There was an error while tuning on [%s]." % (bdid))

            logging.exception(message)
            raise Exception(message)

    def tune(self, tid, name, freq, mod, vid, aid, pid):
        """Tune a channel.

        tid: Tuner ID.
        name: Name of channel.
        freq: Frequency of channel.
        mod: Modulation of channel.
        vid: VideoID
        aid: AudioID
        pid: ProgramID
        """

        try:
            tuner = TunerInfo.build_from_id(tid)

        #tuner.easy_set_vchannel
        except:
            message = "Error while trying to tune."
            
            logging.exception(message)
            raise Exception(message)

    def status(self):
        try:
            response = {}
            for tuner in _tuner.get_statuses().keys():
                device = tuner.device
                driver = device.driver
                
                driver_class_name = driver.__class__.__name__
                if driver_class_name not in response:
                    response[driver_class_name] = {}
                
                device_big_id_str = str(get_big_id_from_device(device))
                tuner_id = tuner.identifier
    
                if device_big_id_str not in response[driver_class_name]:
                    response[driver_class_name][device_big_id_str] = [tuner_id]
                else:
                    response[driver_class_name][device_big_id_str].append(tuner_id)
    
            return response
        except:
            message = "Error while trying to find tuning statuses."

            logging.exception(message)
            raise Exception(message)
