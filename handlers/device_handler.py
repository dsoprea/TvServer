from handlers import GetHandler
from device.drivers import available_drivers
from cache import Cache


class DeviceHandler(GetHandler):
    def list(self, dcn):
        """Find devices for the given driver.

        dcn: Driver class name
        """

        (driver_cls, device_cls) = available_drivers[dcn]
        devices_raw = driver_cls().enumerate_devices()

        devices = {}
        for device in devices_raw:
            device_info = { 'address': device.address, \
                            'tuner_quantity': device.tuner_quantity, \
                            'adapter_index': device.adapter_index }

            devices[device.identifier] = device_info

        Cache().set(str("drivers-%s-devices" % (dcn)), devices, 3600)

        return self.json_response(devices)

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


