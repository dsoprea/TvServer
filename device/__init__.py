class DeviceException(Exception):
    pass

class DriverRequirementsError(DeviceException):
    pass

class DriverConfigurationError(DeviceException):
    pass

class DeviceDoesNotExist(DeviceException):
    pass

class NoTunersAvailable(DeviceException):
    pass

class TunerNotAllocated(DeviceException):
    pass

