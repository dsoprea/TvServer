from tv_server.device.drivers import available_drivers, get_big_id_from_device
from tv_server.backend.protocol.device_list_pb2 import device_listresponse


class DeviceHandler(object):
    def handleList(self, message):
        """Find devices for the given driver.

        dcn: Driver class name
        """

        (driver_cls, device_cls) = available_drivers[message.dcn]
        devices_raw = driver_cls().enumerate_devices()

        response = device_listresponse()
        response.version = 1
        response.success = True

        for device in devices_raw:
            device_msg = response.devices.add() 
            device_msg.bdid = repr(get_big_id_from_device(device))
            device_msg.address = device.address
            device_msg.tuner_quantity = device.tuner_quantity

        return response

