import handlers

from handlers.driver_handler import DriverHandler
#from handlers.device_handler import DeviceHandler
#from handlers.experience_handler import ExperienceHandler

# We used several simpler rules, rather than more ambiguous RXs.
urls = (
    '/driver/([^/]+)(/(.+))?', 'driver',
    '/device/([^/]+)(/(.+))?', 'device',
    '/xp/([^/]+)(/(.+))?', 'experience',
    '/(.*)', 'fail',
)

mapping = { 'fail': handlers.Fail,
            'driver': DriverHandler,
            #'device': DeviceHandler,
            #'experience': ExperienceHandler,
          }
