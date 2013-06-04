from threading import Lock, RLock

from rain_config import values

from rain.common.modules import cf
from rain.dvr.interfaces.device.ituner import ITuner
from rain.dvr.interfaces.device.ituner import *
from rain.dvr.modules.device.utility import get_tuner_index
from rain.dvr.modules.device.tuner_info import TunerInfo

from logging import getLogger
logging = getLogger(__name__)

class Tuner(ITuner):
    """Controls some tuner functionality."""

    __device_store = None

# TODO: Set this back to zero. 
    # We can't move this constant into the config, because, as a component,
    # this can be overridable with alternate functionality. Values specific to
    # this component need to stay in this component.
    #
    # This is zero-based.
    __default_index = 1

    __allocations = None
    __global_listeners = None

    def __init__(self):
        self.__device_store = cf.get(values.C_DEV_STORAGE)

        self.__allocations = {}
        self.__global_listeners = []

        self.update_tuners()
# TODO: Make sure that this gets called.
    def update_tuners(self):
        """Load any missing tuners into allocations, and remove anything that's 
        no longer configured.
        """

        logging.debug("Populating tuner-management object with list of "
                      "devices.")

        try:
            devices = self.__device_store.retrieve_list()
        except:
            logging.exception("Could not retrieve devices.")
            raise

        with Tuner.tuner_locker:

            # Determine which devices no longer exist.
            for device, tuner_allocations in self.__allocations.items():
                if device not in devices:

                    # Check each tuner slot for whether or not it's allocated.
                    for tuner_index in xrange(len(tuner_allocations)):

                        # If the tuner is currently allocated, release it.
                        if tuner_allocations[tuner_index][0]:
                            try:
                                self.release_tuner(device, tuner_index)
                            except:
                                logging.exception("There was an error while "
                                                  "deregistering tuner-index (%d) "
                                                  "on stale device [%s]." % 
                                                  (tuner_index, device))
                                raise

                    # Remove the allocation slots for this device.
                    del self.__allocations[device]

            # Add new devices.
            for device in devices:
                if device not in self.__allocations.keys():
                    # For each device, allow for allocation-data (set when 
                    # allocated), along with a list of event listeners.

                    self.__allocations[device] = []
                    for tuner_index in xrange(device.tuner_quantity):
                        self.__allocations[device].append([None, []])

    def get_default_tuner_index(self, device):
        """When a tuner is required, start with the index that we return."""
        
        # We do a MOD so that we can have a system-default, but never overflow 
        # the number of tuners.
        index = (self.__default_index % device.tuner_quantity)
        
        logging.debug("Returning default tuner-index (%d)." % (index))
        
        return index
        
    def get_next_tuner_index(self, device, current_index):
        """When another tuner is required, return the next one to be 
        used/attempted.
        """

        next_index = (current_index + 1) % (device.tuner_quantity)

        logging.debug("Return next tuner-index (%d) from (%d)." % 
                      (next_index, current_index))

        return next_index

    def __get_allocations_entry(self, specific_tuner):

        device = specific_tuner.device
        tuner_index = specific_tuner.tuner_index

        if device not in self.__allocations:
            return False

        if tuner_index >= len(self.__allocations[device]):
            return False

        return self.__allocations[device][tuner_index]

    def register_listener(self, update_cb, specific_tuner=None):
        """Subscribe a listener to receive tuner changes."""

        with Tuner.tuner_locker:
            if specific_tuner:
                entry = self.__get_allocations_entry(specific_tuner)

                if not entry:
                    return False

                entry[1].append(update_cb)

            else:
                self.__global_listeners.append(update_cb)

        return True

    def remove_listener(self, update_cb, specific_tuner=None):
        """Unsubscribe a listener from receiving tuner changes."""

        with Tuner.tuner_locker:
            if specific_tuner:
                entry = self.__get_allocations_entry(specific_tuner)

                if not entry:
                    return False

                if update_cb not in entry[1]:
                    return False

                entry[1].remove(update_cb)

            else:
                if update_cb not in self.__global_listeners:
                    return False

                self.__global_listeners.remove(update_cb)

        return True

    def __touch_listeners(self, activity_type, specific_tuner=None, data=None):

        with Tuner.tuner_locker:
            if specific_tuner:
                entry = self.__get_allocations_entry(specific_tuner)
                listeners = entry[1] + self.__global_listeners
            else:
                listeners = self.__global_listeners

            try:
# TODO: Make this asynchronous.
                for listener in listeners:
                    listener(activity_type, specific_tuner, data)
            except:
                logging.exception("Listener has failed for tuner-index (%d) on "
                                 "device [%s]." % (specific_tuner.tuner_index, 
                                                   specific_tuner.device))
                raise

    def request_tuner(self, allocation_data=None, specific_driver_name=None, 
                      specific_device=None):
        """Reserve the first available tuner for the requester."""

        self.update_tuners()

        with Tuner.tuner_locker:

            # Run through each tuner on each device until we get an available 
            # one.

            for device, tuner_allocations in self.__allocations.items():
                # If we wanted to request on a specific device and this isn't
                # it, skip.

                if specific_device and device.identifier != specific_device.identifier:
                    continue

                # If we wanted to constrain devices by driver and the driver is
                # wrong, skip.
                elif specific_driver_name != None and \
                     device.driver.__class__.__name__ != specific_driver_name:
                    continue
            
                used = []
                for tuner_index in xrange(len(tuner_allocations)):
                    entry = tuner_allocations[tuner_index]

                    if entry[0] != None:
                        used.append(tuner_index)

                try:            
                    elected = get_tuner_index(device, used)
                except:
                    logging.exception("Could not acquire tuner index for "
                                      "device [%s] with exclude list [%s]." % 
                                      (device, ','.join([str(one_used) \
                                                         for one_used \
                                                         in used])))
                    raise
                
                if elected != None:
                
                    # allocation_data must not evaluate to False.
                    if allocation_data == None:
                        allocation_data = (None,)

                    self.__allocations[device][elected][0] = allocation_data
                    specific_tuner = TunerInfo(device, elected)

                    try:
                        self.__touch_listeners(A_ALLOCATED, specific_tuner, \
                                               allocation_data)
                    except:
                        logging.exception("Touch-listener failed for tuner-"
                                          "index (%d) on device [%s] "
                                          "(allocate)." % (elected, device))
                        raise

                    return specific_tuner

        return None    

    def post_tuner_activity(self, specific_tuner, activity_type):
        """This is meant to receive phase updates during the tuning process."""

        logging.debug("Posting tuner state [%s] for tuner [%s]." % 
                      (activity_type, specific_tuner))

        if activity_type not in TUNER_ACTIVITY_TYPES:
            raise KeyError("Could not post tuner activity of type [%s]." % 
                           (activity_type))

        print("Posting tuner state [%s] for tuner [%s]." % 
                      (activity_type, specific_tuner))
        entry = self.__get_allocations_entry(specific_tuner)

        if not entry:
            return False

        (allocation_data, _) = entry

        if allocation_data == None:
            return False

        try:
            self.__touch_listeners(activity_type, specific_tuner, \
                                   allocation_data)
        except:
            logging.exception("Touch-listener failed for tuner-index (%d) "
                              "on device [%s] (status change)." % 
                              (tuner_index, device))
            raise

    def release_tuner(self, specific_tuner):
        """Indicate that the given tuner should be made available."""

        with Tuner.tuner_locker:
            entry = self.__get_allocations_entry(specific_tuner)

            if not entry:
                return False

            (allocation_data, _) = entry

            if allocation_data == None:
                return False

            # Clear allocation.
            entry[0] = None

            try:
                self.__touch_listeners(A_RELEASED, specific_tuner, \
                                       allocation_data)
            except:
                logging.exception("Touch-listener failed for tuner-index (%d) "
                                  "on device [%s] (release)." % (tuner_index, 
                                                                 device))
                raise

    def get_statuses(self):
        """Get a list of two-tuples and the allocation-data assigned to 
        allocated tuners.
        """
    
        statuses = {}
        for device, tuner_allocation in self.__allocations.iteritems():
            for tuner_index in xrange(len(tuner_allocation)):
                specific_tuner = TunerInfo(device, tuner_index)
                statuses[specific_tuner] = tuner_allocation[tuner_index]

        return statuses

Tuner.tuner_locker = RLock()

