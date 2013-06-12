from tv_server import handlers

from tv_server.handlers.driver_handler import DriverHandler
from tv_server.handlers.device_handler import DeviceHandler
from tv_server.handlers.tuner_handler import TunerHandler

# We used several simpler rules, rather than more ambiguous RXs.
urls = (
    '/driver/([^/]+)(/(.+))?', 'driver',
    '/device/([^/]+)(/(.+))?', 'device',
    '/xp/([^/]+)(/(.+))?', 'experience',
    '/tuner/([^/]+)(/(.+))?', 'tuner',
    '/(.*)', 'fail',
)

mapping = { 'fail': handlers.Fail,
            'driver': DriverHandler,
            'device': DeviceHandler,
            #'experience': ExperienceHandler,
            'tuner': TunerHandler,
          }
