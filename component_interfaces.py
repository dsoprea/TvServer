import values

from interfaces.isignalhook import ISignalHook
from interfaces.device.ituner import ITuner

from logging import getLogger
logging = getLogger(__name__)

_requirements = { 
     values.C_DEV_TUNER: ITuner,
     values.C_SIGNALHOOK: ISignalHook,
}

def get(name):
    try:
        return _requirements[name]
    except:
        logging.exception("No component interface requirement found with name "
                          "[%s]." % (name))
        raise
