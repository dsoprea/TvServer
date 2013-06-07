class ISignalHook(object):
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

    def register_standard(self, event_name, callback):
        """Register a handler for a standard event."""
    
        raise NotImplementedError()

    def unregister_standard(self, event_name, callback):
        """Unregister a standard handler."""

        raise NotImplementedError()

    def register_aggregate_handler(self, event_name, callback):
        """Register a handler for a data-aggregate event."""
    
        raise NotImplementedError()

    def unregister_aggregate_handler(self, event_name, callback):
        """Unregister a data-aggregate handler."""

        raise NotImplementedError()

    def set_aggregate_data(self, event_name, value, key=None):
        """Set the data associated with a data-aggregate event. If a key is not 
        provided, it is to be randomly generated.
        """
    
        raise NotImplementedError()

    def trigger(self, event_name, event_data=None):
        """Trigger an event. Spawn a thread to invoke all of the callbacks 
        asynchronously.
        """

        raise NotImplementedError()

