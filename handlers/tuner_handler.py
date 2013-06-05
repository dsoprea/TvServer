from handlers import GetHandler, decode_fq_device_id, encode_fq_device_id
from device.drivers import available_drivers
from device.tuner import Tuner
from device.tuner_info import TunerInfo
from device import NoTunersAvailable

_tuner = Tuner()


class TunerHandler(GetHandler):
    def acquire(self, did):
        """Acquire exclusive access to a tuner, prior to tuning.
        
        did: Fully-qualified device-ID.
        """

        try:
            (driver_class_name, device_id) = decode_fq_device_id(did)
            driver = available_drivers[driver_class_name][0]
            device = driver().build_from_id(device_id)
    
            tuner = _tuner.request_tuner(specific_device=device)
            if tuner is None:
                raise NoTunersAvailable("No tuners are available on device "
                                        "[%s]." % (did))
            
            return TunerInfo.serialize(tuner)
        except NoTunersAvailable:
            raise
        except:
            raise Exception("There was an error while tuning on [%s]." % (did))

    def tune(self, tuner, name, freq, mod, vid, aid, pid):
        """Tune a channel.

        did: Device ID.
        name: Name of channel.
        freq: Frequency of channel.
        mod: Modulation of channel.
        vid: VideoID
        aid: AudioID
        pid: ProgramID
        """

        tuner = TunerInfo.unserialize(tuner)

        #tuner.easy_set_vchannel

    def status(self):
        response = {}
        for tuner in _tuner.get_statuses().keys():
            device = tuner.device
            driver = device.driver
            
            driver_class_name = driver.__class__.__name__
            if driver_class_name not in response:
                response[driver_class_name] = {}
            
            fq_device_id = encode_fq_device_id(driver_class_name, 
                                               device.identifier)

            tuner_id = TunerInfo.serialize(tuner)

            if fq_device_id not in response[driver_class_name]:
                response[driver_class_name][fq_device_id] = [tuner_id]
            else:
                response[driver_class_name][fq_device_id].append(tuner_id)

        return response
