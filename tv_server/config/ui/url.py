import web

from tv_server import handlers

from tv_server.handlers.driver_handler import DriverHandler
from tv_server.handlers.device_handler import DeviceHandler
from tv_server.handlers.tuner_handler import TunerHandler

# We used several simpler rules, rather than more ambiguous RXs.
urls = (
    '^/favicon.ico$', 'favicon',

    '/driver/([^/]+)(/(.+))?', 'driver',
    '/device/([^/]+)(/(.+))?', 'device',
    '/xp/([^/]+)(/(.+))?', 'experience',
    '/tuner/([^/]+)(/(.+))?', 'tuner',
    '/(.*)', 'fail',
)

class favicon:
    def GET(self):
        raise web.seeother('/static/images/favicon.ico')

mapping = { 'favicon': favicon,
            'fail': handlers.Fail,
            'driver': DriverHandler,
            'device': DeviceHandler,
            #'experience': ExperienceHandler,
            'tuner': TunerHandler,
          }
