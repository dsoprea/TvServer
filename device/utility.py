from rain_config import values
from rain.common.modules import cf

from logging import getLogger
logging = getLogger(__name__)

def get_tuner_index(device, exclude=[]):
    """Return the tuner-index to use, optionally excluding those in the given
    list. Returns None if all are consumed.
    """

    logging.info("Getting tuner index given exclude list [%s] with device "
                 "[%s]." % (','.join([str(one_excluded) for one_excluded \
                                                        in exclude]), device))

    tuner = cf.get(values.C_DEV_TUNER)
    
    # Find a tuner that's not used. In the event that we later outsource the
    # functionality to driver-defined functionality, we keep track of what 
    # we've tried to prevent cycles.

    tuners = range(device.tuner_quantity)
    candidate = tuner.get_default_tuner_index(device)

    tuners.remove(candidate)

    found = False
    i = device.tuner_quantity
    while i > 0:
        # Current candidate is electable.    
        if candidate not in exclude:
            found = True
            break

        # No more tuners are available to be picked from.
        if not tuners:
            break

        # The assumption that this will never return the same tuner if 
        # (i < (num_tuners - 1)).
        candidate = tuner.get_next_tuner_index(device, candidate)
        
        tuners.remove(candidate)
        i -= 1

    return candidate if found else None

