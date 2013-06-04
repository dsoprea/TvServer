
class ITunerDevice(object):
    """Represents a single available device."""
    
    @property
    def driver(self):
        """Returns the driver that represents us."""
    
        raise NotImplementedError()

    @property
    def identifier(self):
        """Return a unique identifer for this device."""
    
        raise NotImplementedError()
        
    @property
    def address(self):
        """Returns the network address, memory location, etc.., where this 
        device is listening.
        """
    
        raise NotImplementedError()

    @property
    def junk_data(self):
        """Returns an object of an unspecified type that the driver knows how 
        to interpret. Used for implementation-specific data to be passed from
        the device to the driver.
        """

        raise NotImplementedError()

    @property
    def tuner_quantity(self):
        """Returns the number of tuners available on the device."""
        
        raise NotImplementedError()

    def __hash__(self):
        """Returns a unique string for this device."""
# TODO: This needs to implement priority.    
        raise NotImplementedError()
        
    def __cmp__(self, o):
        """Returns 0 if <self> equals <o>, and -1 otherwise."""
    
        raise NotImplementedError()

    @property
    def supported_channelliststypes(self):
        """Return the support channel-list classes that we support for tuning.
        """
        
        raise NotImplementedError()

    @property
    def channellist(self):
        """Return an instance of the IChannelList that we currently tune with.
        """
    
        raise NotImplementedError()

    @channellist.setter
    def channellist(self, channellist):
        """Set a new instance of an IChannelList to tune with."""

        raise NotImplementedError()

