import logging

from handlers import GetHandler
from device.drivers import available_drivers


class DriverHandler(GetHandler):
    def list(self):
        try:
            distilled = {}
            for pair in available_drivers.iteritems():
                (driver_cls_name, (driver_cls, device_cls)) = pair
    
                driver = driver_cls()
                distilled[driver_cls_name] = (driver.name, driver.description)
    
            return distilled
        except:
            message = "Could not list drivers."

            logging.exception(message)
            raise Exception(message)

    def info(self, dcn):
        try:
            (driver_cls, device_cls) = available_drivers[dcn]
    
            info = { 'supports_channelscan': \
                        driver_cls().supports_channelscan }
    
            return info
        except:
            message = ("Could not show information for driver [%s]." % (dcn))

            logging.exception(message)
            raise Exception(message)
