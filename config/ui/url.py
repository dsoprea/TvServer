import handlers

from handlers.driver_handler import DriverHandler
from handlers.device_handler import DeviceHandler
#from handlers.experience_handler import ExperienceHandler
from handlers.tuner_handler import TunerHandler

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
