from interfaces.idictable import IDictable

class IChannelList(IDictable):
    """Describes a list of channels."""

    @staticmethod
    def get_required_textfields():
        """Return a ITextFields object."""
        
        raise NotImplementedError()

    @staticmethod
    def factory(field_values):
        """Build an instance using a populated ITextFields object."""
        
        raise NotImplementedError()

    @property
    def list(self):
        """Return a PrimitiveChannelList object."""
    
        raise NotImplementedError()

    @list.setter
    def list(self):
        """Set a PrimitiveChannelList object. This will only be used for those 
        IChannelList classes where channels_are_managed() returns True.
        """
    
        raise NotImplementedError()

    @property
    def name(self):
        """Return the name given to this channel-list."""
        
        raise NotImplementedError()

    @property
    def requires_scan(self):
        """Returns boolean indicating whether this channel-list relies on a 
        channel-scan being performed.
        """

        raise NotImplementedError()

    @property
    def channels_are_managed(self):
        """Returns a boolean indicating whether the platform is keeping track
        of the channels, and should load the channels. Else, this class should
        do this internally.
        """
    
        raise NotImplementedError()

