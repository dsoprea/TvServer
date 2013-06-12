from tv_server.interfaces.idictable import IDictable

# "Tune-Data Type"
TD_TYPE_VCHANNEL = 'vchannel'
TD_TYPE_CHANNELSCONF = 'channelsconf'


class ITunerDriver(IDictable):#, IPanelSource):
    """Represents an interface to a particular class of TV tuner."""

    def enumerate_devices(self):
        """List available devices."""

        raise NotImplementedError()

    def build_from_id(self, id_):
        """Build a device given its ID. The ID should implement everything we 
        need to reconstitute.
        """
    
        raise NotImplementedError()
        
    def is_available(self, device):
        """Check if the given device is still available."""
    
        raise NotImplementedError()

    def check_tuning_status(self, tuner):
        """Return True if the channel is still tuned properly or False, 
        otherwise.
        """
    
        raise NotImplementedError()

    def set_tune(self, tuner, param, target):
        """Set the vchannel on the given tuner with the given parameter, which
        depends on the value of tuner_data_type."""
    
        raise NotImplementedError()

    def clear_tune(self, tuner):
        """Stop the given currently-tuned tuner."""
    
        raise NotImplementedError()

    @property
    def name(self):
        """Returns a nice, human-readable name for this driver."""
        
        raise NotImplementedError()

    @property
    def description(self):
        """Returns a string that describes the type of device that we handle.
        """
        
        raise NotImplementedError()

    @property
    def tuner_data_type(self):
        """Returns one of the TD_TYPE_* values (above)."""

        raise NotImplementedError()

    @property
    def stream_mimetype(self):
        return "video/mpeg2"

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, o):
        return (hash(self) == hash(o)) 

    def __ne__(self, o):
        return (hash(self) != hash(o))
