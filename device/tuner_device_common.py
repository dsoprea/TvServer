from logging import getLogger
logging = getLogger(__name__)

class TunerDeviceCommon(object):

    def device_id(self):
        """Returns a device-unique ID."""

        return ('%s,%s' % (self.driver.name, self.address)).__hash__()

    def __hash__(self):
        """Returns a unique string for this device. Required to be Hashable."""

        return self.device_id()

    def __cmp__(self, o):
        """Returns 0 if <self> equals <o>, and -1 otherwise. Required to be
        Hashable.
        """

        if o == None:
            return -1

        return (0 if self.device_id() == o.device_id() else -1)

