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
            raise Exception("Could not list drivers.")

    def info(self, dcn):
        try:
            (driver_cls, device_cls) = available_drivers[dcn]
            driver = driver_cls()
    
            info = { 'supports_channelscan': driver.supports_channelscan }
    
            return info
        except:
            raise Exception("Could not show information for driver [%s]." % 
                            (dcn))
