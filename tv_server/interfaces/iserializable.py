class ISerializable(object):
    @staticmethod
    def serialize(obj):
        """Reduce the given object to a string."""

        raise NotImplementedError()
    
    @staticmethod
    def unserialize(data):
        """Restore an object from a string."""

        raise NotImplementedError()

