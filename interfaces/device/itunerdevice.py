
class ITunerDevice(object):
    """Represents a single available device."""
    
    @property
    def driver(self):
        """Returns the driver that represents us."""
    
        raise NotImplementedError()

    @property
    def identifier(self):
        """Return a unique identifer for this device. It must embed any 
        information necessary to reconstitute the device."""
    
        raise NotImplementedError()
        
    @property
    def address(self):
        """Returns the network address, memory location, etc.., where this 
        device is listening.
        """
    
        raise NotImplementedError()

    @property
    def tuner_quantity(self):
        """Returns the number of tuners available on the device."""
        
        raise NotImplementedError()
# TODO: Deimplement junk_data.
    @property
    def junk_data(self):
        """Returns an object of an unspecified type that the driver knows how 
        to interpret. Used for implementation-specific data to be passed from
        the device to the driver.
        """

        raise NotImplementedError()

    def __cmp__(self, o):
        """Returns 0 if <self> equals <o>, and -1 otherwise."""
    
        raise NotImplementedError()

    def __hash__(self):
        raise NotImplementedError()

    def __eq__(self, o):
        raise NotImplementedError()

    def __ne__(self, o):
        raise NotImplementedError()
