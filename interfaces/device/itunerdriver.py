from interfaces.idictable import IDictable
#from rain.dvr.ui.interfaces.ipanelsource import IPanelSource

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

    def iterate_channels_start(self, device, tuner_index, channel_map):
        """Establish the initial state information for a channel-scan. As 
        opposed to the generator function, this allows the caller to stash the
        state value and each, next, successive channel at some unspecified time
        in the future. Returns a blackbox state object.
        """

        raise NotImplementedError()

    def iterate_channels_next(self, state):
        """Take the object returned by iterate_channels_start and scan the next
        channel. Returns False if done, None if channel is to be skipped, or
        "(progress_int, ChannelInfo, <ProgramInfo[]>)" if channel successfully 
        locked.
        """

        raise NotImplementedError()

    def check_tuning_status(self, tuner):
        """Return True if the channel is still tuned properly or False, 
        otherwise.
        """
    
        raise NotImplementedError()

    def set_vchannel(self, tuner, vchannel_scalar=None):
        """Set the vchannel on the given tuner to the given scalar."""
    
        raise NotImplementedError()

    def capture_to_file(self, tuner, writer):
        """Start streaming the feed."""

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
    def transport_info(self):
        """Returns a description of the media stream."""

        raise NotImplementedError()

    @property
    def supports_channelscan(self):
        """Returns a boolean expressing whether a channel-scan is both 
        supported and required. A driver that doesn't support a manual channel-
        scan must have some other method of determining channels, such as 
        having been given a channels.conf file.
        """
        
        raise NotImplementedError()

