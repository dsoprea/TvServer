from tv_server.handlers import GetHandler
from tv_server.backend.protocol.devicelist_pb2 import devicelist
from tv_server.backend.protocol.error_pb2 import error
from tv_server.backend.client import Client
from tv_server.handlers import RequestError


class DeviceHandler(GetHandler):
    def __init__(self):
        super(DeviceHandler, self).__init__()
        self.__client = Client()
        
    def list(self, dcn):
        """Find devices for the given driver.

        dcn: Driver class name
        """

        devicelist_msg = devicelist()
        devicelist_msg.version = 1
        devicelist_msg.dcn = dcn

        response = self.__client.send_query(devicelist_msg)
        if response.__class__ == error or response.success == False:
            raise RequestError("Device-list failed: %s" % (response.message))

        devices = {}
        for device in response.devices:
            device_info = { 'address': device.address, \
                            'tuner_quantity': device.tuner_quantity }

            devices[device.bdid] = device_info

        return devices
