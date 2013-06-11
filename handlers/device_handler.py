import logging

from handlers import GetHandler, RequestError
from device.drivers import available_drivers, get_big_id_from_device
#from cache import Cache

# TODO: Move request handling logic to backend. 


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
                                'tuner_quantity': device.tuner_quantity }
    
                big_device_id = get_big_id_from_device(device)
                devices[repr(big_device_id)] = device_info
    
#            Cache().set(str("tv-drivers-%s-devices" % (dcn)), devices, 3600)
        except RequestError:
            raise
        except:
            message = ("There was an error while trying to list devices for "
                       "driver [%s]." % (dcn))

            logging.exception(message)
            raise Exception(message)

        return devices
