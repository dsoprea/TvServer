class IChannelStorage(object):
    """The mechanism responsible for persisting channel information."""

    def get_channellist_types(self):
        """Return a dictionary of type names to type classes."""

        raise NotImplementedError()

    def store_channellist(self, channellist):
        """Store or replace the given IChannelList."""

        raise NotImplementedError()

    def remove_channellist(self, name):
        """Remove the channel-list from storage."""

        raise NotImplementedError()

    def get_channellist(self, name):

        raise NotImplementedError()

    def get_channellists(self):
        """Get a list of the channel-lists that have been stored."""

        raise NotImplementedError()

    def set_channellist_mapping(self, device, channellist):
        """Assign the given channel-list to the given device."""

        raise NotImplementedError()

    def clear_channellist_mapping_by_device(self, device):
        """Clear the channel-list mapping for the given device."""

        raise NotImplementedError()

    def clear_channellist_mapping_by_channellist(self, channellist):
        """Clear the channel-list mapping for any device mapped to the given
        channel-list.
        """

        raise NotImplementedError()

