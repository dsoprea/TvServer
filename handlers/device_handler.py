from handlers import GetHandler
from device.drivers import available_drivers, get_big_id_from_device

# TODO: Move request handling logic to backend. 


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
                            'tuner_quantity': device.tuner_quantity }

            big_device_id = get_big_id_from_device(device)
            devices[repr(big_device_id)] = device_info

        return devices
