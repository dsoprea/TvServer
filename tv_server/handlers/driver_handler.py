from tv_server.handlers import GetHandler, RequestError
from tv_server.device.drivers import available_drivers


class DriverHandler(GetHandler):
    def list(self):
        distilled = {}
        for pair in available_drivers.iteritems():
            (driver_cls_name, (driver_cls, device_cls)) = pair

            driver = driver_cls()
            distilled[driver_cls_name] = (driver.name, driver.description)

        return distilled

    def info(self, dcn):
        (driver_cls, device_cls) = available_drivers[dcn]

        driver = driver_cls()
        info = { 'tune_type': \
                    driver.tuner_data_type,
                 'stream_mimetype':
                    driver.stream_mimetype }

        return info
