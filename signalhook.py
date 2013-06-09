from threading import Thread
from time import time
from random import randrange

from interfaces.isignalhook import ISignalHook
from utility import get_caller

from logging import getLogger
logging = getLogger(__name__)

class _EventInstance(Thread):
    """A thread class that handles invoking all of the event callbacks."""

    def __init__(self, event_name, handlers, aggregates, event_data):
        thread_name = ("%s-%f" % (event_name, time()))
        
        Thread.__init__(self, name=thread_name)

        self.__event_name = event_name
        self.__handlers   = handlers
        self.__aggregates = aggregates
        self.__event_data = event_data

    def handle_event(self):
        """This might be called directly if the event is supposed to be 
        synchronous.
        """
    
        aggregates_count = len(self.__aggregates[1]) \
                            if self.__aggregates \
                            else 0

        logging.debug("Event [%s] being handled. There are (%d) standard "
                      "handlers and (%d) data-aggregate handlers." % 
                      (self.__event_name, len(self.__handlers), 
                       aggregates_count))

        i = 0
        for handler in self.__handlers:
            try:
                handler(self.__event_data)
            except:
                logging.exception("Event [%s] handler [%s](%d) threw an "
                                  "exception." % (self.__event_name, handler, i))

            i += 1

        if self.__aggregates:
            (data, handlers) = self.__aggregates
            
            i = 0
            for handler in handlers:
                try:
                    handler(data, self.__event_data)
                except:
                    logging.exception("Event [%s] data-aggregate handler [%s](%d) "
                                      "threw an exception." % (self.__event_name, 
                                                               handler, i))

                i += 1

        logging.debug("Handling of event [%s] complete." % (self.__event_name))

    def run(self):

        self.handle_event()

class SignalHook(ISignalHook):
    """SignalHook is an eventing coordination facility. It's meant for internal 
    broadcasts of software events (such as shutdown), meant to trigger the 
    callbacks that are registered for certain event types. It is not meant to 
    be confused with the messaging system, and only influencing the current
    process. The callbacks are triggered from a separate thread.
    
    Two types of events can be managed:
    > standard handler:       Registered callbacks are triggered upon each 
                              event.
    > data aggregate handler: Data is registered, and each callback is passed 
                              the dictionary of data upon each event.
    """

    def __init__(self):
        self.__standard_handlers = {}
        self.__data_aggregates   = {}

    def register_standard(self, event_name, callback):
        """Register a handler for a standard event."""
    
        if event_name not in self.__standard_handlers:
            self.__standard_handlers[event_name] = []

        if callback not in self.__standard_handlers[event_name]:
            self.__standard_handlers[event_name].append(callback)

    def unregister_standard(self, event_name, callback):
        """Unregister a standard handler."""
    
        if event_name not in self.__standard_handlers:
            return

        if callback in self.__standard_handlers[event_name]:
            self.__standard_handlers[event_name].remove(callback)

    def __ensure_data_aggregate(self, event_name):
        if event_name not in self.__data_aggregates:
            self.__data_aggregates[event_name] = ({}, [])

    def register_aggregate_handler(self, event_name, callback):
        """Register a handler for a data-aggregate event."""
    
        self.__ensure_data_aggregate(event_name)

        if callback not in self.__data_aggregates[event_name][1]:
            self.__data_aggregates[event_name][1].append(callback)

    def unregister_aggregate_handler(self, event_name, callback):
        """Unregister a data-aggregate handler."""

        if event_name not in self.__data_aggregates:
            return

        if callback in self.__data_aggregates[event_name][1]:
            self.__data_aggregates[event_name][1].remove(callback)

    def set_aggregate_data(self, event_name, value, key=None):
        """Set the data associated with a data-aggregate event."""

        self.__ensure_data_aggregate(event_name)

        if key == None:
            while 1:
                key = ('_%d' % (randrange(11111111, 99999999)))

                if key not in self.__data_aggregates[event_name][0]:
                    break

        self.__data_aggregates[event_name][0][key] = value

    def trigger(self, event_name, event_data=None, synchronous=False):
        """Trigger an event. Spawn a thread to invoke all of the callbacks 
        asynchronously.
        """

        caller_name = get_caller()[3]

        logging.info("Triggering event [%s] from [%s].  SYNC= [%s]  "
                     "HAS-DATA= [%s]" % (event_name, caller_name, 
                                         bool(synchronous), bool(event_data)))
    
        standard_handlers = self.__standard_handlers[event_name] \
                                if event_name in self.__standard_handlers \
                                else []

        data_aggregates = self.__data_aggregates[event_name] \
                            if event_name in self.__data_aggregates \
                            else None

        if not standard_handlers and not data_aggregates:
            logging.debug("No callbacks are registered for event-name [%s]." % 
                          (event_name))
            return
        
        invoker = _EventInstance(event_name,
                                 standard_handlers,
                                 data_aggregates,
                                 event_data)

        if synchronous:
            invoker.handle_event()
        else:
            invoker.start()

