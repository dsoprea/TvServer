
class IDriverDiscovery(object):
    """Driver-related functionality."""

    def get_available_drivers(self):
        """Returns a dictionary of names to class types. Classes must 
        implemented ITunerDriver.
        """

        raise NotImplementedError()

