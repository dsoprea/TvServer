from handlers import GetHandler, decode_fq_device_id
from device.drivers import available_drivers
from device.tuner import Tuner
from device.tuner_info import TunerInfo
from device import NoTunersAvailable

_tuner = Tuner()


class TunerHandler(GetHandler):
    def tune(self, did, name, freq, mod, vid, aid, pid):
        """Tune a channel given the tuning parameters.

        did: Device ID.
        name: Name of channel.
        freq: Frequency of channel.
        mod: Modulation of channel.
        vid: VideoID
        aid: AudioID
        pid: ProgramID
        """

        try:
            (driver_class_name, device_id) = decode_fq_device_id(did)
            driver = available_drivers[driver_class_name][0]
            device = driver().build_from_id(device_id)
    
            tuner_info = _tuner.request_tuner(specific_device=device)
            if tuner_info is None:
                raise NoTunersAvailable("No tuners are available on device "
                                        "[%s]." % (did))
            
            return TunerInfo.serialize(tuner_info)
        except NoTunersAvailable:
            raise
        except:
            raise Exception("There was an error while tuning on [%s]." % (did))
