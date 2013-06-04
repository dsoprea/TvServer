
class IMediaArbitration(object):
    """Determines if two formats should be considered identical. Will later
    provide the conversion functionality.
    """

    def find_compatible_storage_profile(self, transport):
        """Determine if there's a compatible transport profile among those 
        supported by the system for storage, and return it, or None if none.
        """

        raise NotImplementedError

    def is_compatible(self, transport_from, transport_to):
        """Returns boolean regarding whether 'transport_from' should be 
        considered equal to 'transport_to' without further conversion.
        """
        
        raise NotImplementedError

    def convert_if_necessary(self, transport_info, storage_profile, \
                             stream_mapping):
        """Determine if any conversion is necessary to get from the mapped
        channels in 'transport_info' to the formats specified in 
        'storage_profile'.
        """
        
        raise NotImplementedError

