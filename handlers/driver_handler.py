from handlers import GetHandler
from device.drivers import available_drivers
from cache import Cache

class DriverHandler(GetHandler):
    def list(self):
        distilled = {}
        for pair in available_drivers.iteritems():
            (driver_cls_name, (driver_cls, device_cls)) = pair

            driver = driver_cls()
            distilled[driver_cls_name] = (driver.name, driver.description)

        return self.json_response(distilled)

    def info(self, dcn):
        (driver_cls, device_cls) = available_drivers[dcn]
        driver = driver_cls()

        info = { 'supports_channelscan': driver.supports_channelscan }

        return self.json_response(info)
