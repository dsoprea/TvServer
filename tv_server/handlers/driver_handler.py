from tv_server.handlers import GetHandler, RequestError
from tv_server.backend.client import Client
from tv_server.backend.protocol.driver_list_pb2 import driver_list
from tv_server.backend.protocol.driver_info_pb2 import driver_info
from tv_server.backend.protocol.error_pb2 import error


class DriverHandler(GetHandler):
    def __init__(self):
        super(DriverHandler, self).__init__()
        self.__client = Client()
        
    def list(self):
        driverlist_msg = driver_list()
        driverlist_msg.version = 1

        response = self.__client.send_query(driverlist_msg)
        if response.__class__ == error or response.success == False:
            raise RequestError("Driver-list failed: %s" % (response.message))

        distilled = {}
        for driver_msg in response.drivers:
            distilled[driver_msg.dcn] = (driver_msg.name, \
                                         driver_msg.description)

        return distilled

    def info(self, dcn):
        driverinfo_msg = driver_info()
        driverinfo_msg.version = 1
        driverinfo_msg.dcn = dcn

        response = self.__client.send_query(driverinfo_msg)
        if response.__class__ == error or response.success == False:
            raise RequestError("Driver-info failed: %s" % (response.message))

        return { 'tune_type': response.tune_type,
                 'stream_mimetype': response.stream_mimetype }

