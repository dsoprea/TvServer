from handlers import GetHandler
from device.drivers import available_drivers
from cache import Cache

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

        pass

