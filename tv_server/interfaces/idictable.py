class IDictable(object):
    @staticmethod
    def convert_to_dict(obj):
        """Reduce the given object to a dictionary."""

        raise NotImplementedError()
    
    @staticmethod
    def convert_from_dict(data):
        """Restore an object from a dictionary."""

        raise NotImplementedError()

