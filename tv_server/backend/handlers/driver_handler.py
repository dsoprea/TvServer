from tv_server.device.drivers import available_drivers
from tv_server.backend.protocol.driver_list_pb2 import driver_listresponse
from tv_server.backend.protocol.driver_info_pb2 import driver_inforesponse


class DriverHandler(object):
    def handleList(self, message):
        response = driver_listresponse()
        response.version = 1
        response.success = True

        for pair in available_drivers.iteritems():
            (driver_cls_name, (driver_cls, device_cls)) = pair
            driver = driver_cls()

            driver_msg = response.drivers.add()
            driver_msg.dcn = driver_cls_name
            driver_msg.name = driver.name
            driver_msg.description = driver.description

        return response

    def handleInfo(self, message):
        (driver_cls, device_cls) = available_drivers[message.dcn]
        driver = driver_cls()
        
        response = driver_inforesponse()
        response.version = 1
        response.success = True
        response.tune_type = driver.tuner_data_type
        response.stream_mimetype = driver.stream_mimetype  
        
        return response
