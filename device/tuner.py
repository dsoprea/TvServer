from threading import Lock, RLock

#from rain_config import values

#from rain.common.modules import cf
from interfaces.device.ituner import ITuner
from interfaces.device.ituner import A_ALLOCATED, A_RELEASED, \
                                     TUNER_ACTIVITY_TYPES
from device.tuner_info import TunerInfo

from logging import getLogger
logging = getLogger(__name__)


class Tuner(ITuner):
    """Manages allocated and available the individual tuners of every device.
    """

    #__device_store = None
    __default_index = 0

    def __init__(self):
        #self.__device_store = cf.get(values.C_DEV_STORAGE)

        # Tuner: (allocation_data, [<listeners>])
        self.__allocations = {}

        self.__global_listeners = []

        self.update_tuners()

    def update_tuners(self, with_device=None):
        """Load any missing tuners into allocations, and remove anything that's 
        no longer configured.
        """

        logging.debug("Populating tuner-management object with list of "
                      "devices.")

#        try:
#            devices = self.__device_store.retrieve_list()
#        except:
#            logging.exception("Could not retrieve devices.")
#            raise

        with Tuner.tuner_locker:

            # Determine which devices no longer exist.
            for device, tuner_allocations in self.__allocations.items():
                if device.driver.is_available(device) is False:

                    # Check each tuner slot for whether or not it's allocated.
                    for tuner_index in xrange(len(tuner_allocations)):

                        # If the tuner is currently allocated, release it.
                        if tuner_allocations[tuner_index][0] is not None:
                            try:
                                self.release_tuner(device, tuner_index)
                            except:
                                logging.exception("There was an error while "
                                                  "deregistering tuner-index "
                                                  "(%d) on stale device "
                                                  "[%s]." %
                                                  (tuner_index, device))
                                raise

                    # Remove the allocation slots for this device.
                    del self.__allocations[device]

            # Add new devices.
            if with_device is not None and \
               with_device not in self.__allocations:
                # For each device, allow for tuner-info (set when allocated), 
                # allocation-data, along with a list of event listeners.
# TODO: Add a hash function to the device and driver classes.
                self.__allocations[with_device] = []
                for tuner_index in xrange(with_device.tuner_quantity):
                    self.__allocations[with_device].append([None, None, []])

    def __get_default_tuner_index(self, device):
        """When a tuner is required, start with the index that we return."""
        
        # We do a MOD so that we can have a system-default, but never overflow 
        # the number of tuners.
        index = (self.__class__.__default_index % device.tuner_quantity)
        
        logging.debug("Returning default tuner-index (%d)." % (index))
        
        return index
        
    def __get_next_tuner_index(self, device, current_index):
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
# TODO: This will not exist unless someone tries to tune it, first (and the
#       update call is made).
                if not entry:
                    return False

                entry[2].append(update_cb)

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

                if update_cb not in entry[2]:
                    return False

                entry[2].remove(update_cb)

            else:
                if update_cb not in self.__global_listeners:
                    return False

                self.__global_listeners.remove(update_cb)

        return True

    def __touch_listeners(self, activity_type, specific_tuner=None, data=None):

        with Tuner.tuner_locker:
            if specific_tuner:
                entry = self.__get_allocations_entry(specific_tuner)
                listeners = entry[2] + self.__global_listeners
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

    def __get_tuner_index(self, device, exclude=[]):
        """Return the tuner-index to use, optionally excluding those in the given
        list. Returns None if all are consumed.
        """
    
        logging.info("Getting tuner index given exclude list [%s] with device "
                     "[%s]." % (','.join([str(one_excluded) for one_excluded \
                                                            in exclude]), device))
    
        # Find a tuner that's not used. In the event that we later outsource the
        # functionality to driver-defined functionality, we keep track of what 
        # we've tried to prevent cycles.
    
        tuners = range(device.tuner_quantity)
        candidate = self.__get_default_tuner_index(device)
    
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
            candidate = self.__get_next_tuner_index(device, candidate)
            
            tuners.remove(candidate)
            i -= 1
    
        return candidate if found else None

    def request_tuner(self, allocation_data=None, specific_driver=None, 
                      specific_device=None):
        """Reserve the first available tuner for the requester."""

        self.update_tuners(specific_device)

        with Tuner.tuner_locker:

            # Run through each tuner on each device until we get an available 
            # one.

            for device, tuner_allocations in self.__allocations.items():
                # If we wanted to request on a specific device and this isn't
                # it, skip. If it matches, we skip the specific_driver check.
                if specific_device is not None:
                    if device.identifier != specific_device.identifier:
                        continue
                # If we wanted to constrain devices by driver and the driver is
                # wrong, skip.
                elif specific_driver is not None and \
                     device.driver.__class__ != specific_driver.__class__:
                    continue
            
                used = []
                for tuner_index in xrange(len(tuner_allocations)):
                    entry = tuner_allocations[tuner_index]

                    if entry[0] is not None:
                        used.append(tuner_index)

                try:
                    elected = self.__get_tuner_index(device, used)
                except:
                    logging.exception("Could not acquire tuner index for "
                                      "device [%s] with exclude list [%s]." % 
                                      (device, ','.join([str(one_used) \
                                                         for one_used \
                                                         in used])))
                    raise
                
                if elected != None:
                
                    specific_tuner = TunerInfo(device, elected)
                    self.__allocations[device][elected][0:2] = \
                        [specific_tuner, allocation_data]

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

        (tuner_info, allocation_data, _) = entry

        if tuner_info == None:
            return False

        try:
            self.__touch_listeners(activity_type, specific_tuner, \
                                   allocation_data)
        except:
            logging.exception("Touch-listener failed for tuner-index (%d) "
                              "on device [%s] (status change)." % 
                              (specific_tuner.tuner_index, 
                               specific_tuner.device))
            raise

    def release_tuner(self, specific_tuner):
        """Indicate that the given tuner should be made available."""

        with Tuner.tuner_locker:
            entry = self.__get_allocations_entry(specific_tuner)

            if not entry:
                return False

            (tuner_info, allocation_data, _) = entry

            if tuner_info is None:
                return False

            # Clear allocation.
            entry[0] = None

            try:
                self.__touch_listeners(A_RELEASED, specific_tuner, \
                                       allocation_data)
            except:
                logging.exception("Touch-listener failed for tuner-index (%d) "
                                  "on device [%s] (release)." % 
                                  (specific_tuner.tuner_index, 
                                   specific_tuner.device))
                raise

    def get_status(self, device, tuner_index):
        """Return a boolean indicating whether a tuner is allocated."""
        
        try:
            return self.__allocations[device][tuner_index] is not None
        except:
            # We no longer know about this device, or a difference device has,
            # somehow, replaced the other one, and it has less tuners.
            return False

    def get_statuses(self):
        """Get a list of two-tuples and the allocation-data assigned to 
        allocated tuners.
        """
    
        statuses = {}
        for device, tuner_allocation in self.__allocations.iteritems():
            device_statuses = []
            for tuner_allocation_info in tuner_allocation:
                if tuner_allocation_info[0] is None:
                    continue

                device_statuses[tuner_allocation_info[0]].\
                    append(tuner_allocation_info[0])

            if device_statuses:
                statuses[device.identifier] = device_statuses

        return statuses

Tuner.tuner_locker = RLock()

