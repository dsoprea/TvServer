from handlers import GetHandler
from device.drivers import available_drivers

class DriverHandler(GetHandler):
    def list_drivers(self):
        distilled = {}
        for driver_cls, device_cls in available_drivers:
            driver = driver_cls()
            distilled[driver.name] = driver.description

        return self.json_response(distilled)
