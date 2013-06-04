
(SF_AVAILABLE, SF_MISSING, SF_BOTH, SF_TUPLE) = range(4)

class IDeviceStorage(object):
    """This class knows how to store available devices."""

    def store_list(self, device_list):
        """Persist the given list of devices."""

        raise NotImplementedError()

    def store(self, device):
        """Persist the given device."""

        raise NotImplementedError()

    def retrieve_by_name(self, identifier):
        """Return a device by name."""

        raise NotImplementedError()

    def retrieve_list(self):
        """Retrieved stored devices. Omit any devices that are no longer 
        available.
        """

        raise NotImplementedError()

