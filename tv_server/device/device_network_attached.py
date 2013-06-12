from tv_server.interfaces.device.itunerdevice import ITunerDevice
from tv_server.device.tuner_device_common import TunerDeviceCommon

from logging import getLogger
logging = getLogger(__name__)

class DeviceNetworkAttached(TunerDeviceCommon, ITunerDevice):
    """Represents a single available network-attached tuner. As the driver does
    any heavy-lifting, this is purely/largely informational."""

    __driver = None
    __ip = None
    __data = None
    __tuner_quantity = None

    def __init__(self, driver, ip, tuner_quantity, data=None):
        self.__driver = driver
        self.__ip = ip
        self.__tuner_quantity = tuner_quantity
        self.__data = data
    
    def __str__(self):
        return ('(DEV-NA) %s(%s-%d)' % (self.__driver.__class__.__name__, 
                                        self.__ip, self.__tuner_quantity))
    
    @property
    def driver(self):
        """Returns the driver that represents us."""
    
        return self.__driver

    @property
    def identifier(self):
        """Return a unique identifer for this device."""
    
        return ('%s(%s)' % (self.__driver.name, self.__ip))
        
    @property
    def address(self):
        """Returns the network address, memory location, etc.., where this 
        device is listening.
        """
    
        return self.__ip

    @property
    def junk_data(self):
        """Returns an object of an unspecified type that the driver knows how 
        to interpret. Used for implementation-specific data to be passed from
        the device to the driver.
        """

        return self.__data

    @property
    def tuner_quantity(self):
        """Returns the number of tuners available on the device."""
        
        return self.__tuner_quantity

