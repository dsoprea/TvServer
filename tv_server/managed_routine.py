from tv_server import values, signals
from tv_server import cf

from logging import getLogger
logging = getLogger(__name__)

signalhook = cf.get(values.C_SIGNALHOOK)

def _shutdown_handler(aggregate_data, event_data):
    """This receives a shutdown request from the process."""

    logging.info("Shutting down (%d) managed routines." % (len(aggregate_data)))

    sorted_info = sorted(aggregate_data.values(), key=lambda info: info[0])
    for (_, routine) in sorted_info:
        logging.debug("Canceling managed-routine [%s]." % (routine.name))
    
        try:
            routine.cancel()
        except:
            logging.exception("Exception while canceling routine [%s]." % 
                              (routine.name))

# Register an aggregate-data handler for the SHUTDOWN event. It will receive
# a list of all managed-routines.
signalhook.register_aggregate_handler(signals.S_SHUTDOWN, _shutdown_handler)

class ManagedRoutine(object):
    """Managed routines provide the ability to properly shutdown when the 
    process is about to end. This is intended to accompany threads and 
    multiprocessing processes.
    """

    __registered = {}

    def __init__(self, name, close_priority=0):
        """'name' is a friendly name for the routine for logging as well as 
        referencing later, and 'close_priority' indicates the order in which it 
        will be closed at shutdown. Lower priorities are canceled first.
        """

        self.__name = name

        info = (close_priority, self)

        # Notify us if the process wants to shutdown.
        signalhook.set_aggregate_data(signals.S_SHUTDOWN, info)
        ManagedRoutine.__registered[name] = info

    def cancel(self):
        """Stop the thread."""

        raise NotImplementedError()

    @property
    def name(self):
        return self.__name

    @staticmethod
    def get_by_prefix(prefix):
        """Return a list of routines whose names are prefixed with the given 
        string.
        """

        matched = {}
        prefix_len = len(prefix)
        for routine_name, routine in ManagedRoutine.__registered.items():
            if routine_name[0:prefix_len] == prefix:
                matched[routine_name] = routine

        return matched

    @staticmethod
    def get_registered():

        return ManagedRoutine.__registered

