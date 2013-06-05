from handlers import GetHandler, encode_fq_device_id
from device.drivers import available_drivers
from cache import Cache


class DeviceHandler(GetHandler):
    def list(self, dcn):
        """Find devices for the given driver.

        dcn: Driver class name
        """

        try:
            (driver_cls, device_cls) = available_drivers[dcn]
            devices_raw = driver_cls().enumerate_devices()
    
            devices = {}
            for device in devices_raw:
                device_info = { 'address': device.address, \
                                'tuner_quantity': device.tuner_quantity, \
                                'adapter_index': device.adapter_index }
    
                fq_device_id = encode_fq_device_id(dcn, device.identifier)
                devices[fq_device_id] = device_info
    
            Cache().set(str("tv-drivers-%s-devices" % (dcn)), devices, 3600)
        except:
            raise Exception("There was an error while trying to list devices "
                            "for driver [%s]." % (dcn))

        return devices
