from rain_config import values
from rain_config.config_namespaces import NS_DEVICE

from rain.common.interfaces.iconfigstore import T_COMPLEX
from rain.common.modules import cf
from rain.common.modules.utility import load_class
from rain.dvr.interfaces.device.idevicestorage import IDeviceStorage, \
                                                      SF_AVAILABLE, \
                                                      SF_MISSING, \
                                                      SF_BOTH, \
                                                      SF_TUPLE

from logging import getLogger
logging = getLogger(__name__)

class DeviceStorage(IDeviceStorage):
    """This class knows how to store available devices."""

    __device_registry = None
    __comment = None

    def __init__(self):
        config_manager = cf.get(values.C_CONFIG)
        self.__device_registry = config_manager.\
                                    get_registry(values.CONF_DEVICE)

        try:
            dbcomments = cf.get(values.C_TEXT_DBCOMMENTS)
            self.__comment = dbcomments.get(['_General'], 'device_comment')
        except LookupError as e:
            message = ("Could not find comment text for configurable: %s" % 
                       (e))
        
            logging.error(message)
            raise Exception(message)
        except:
            logging.exception("Could not find device_comment text.")
            raise

    def store_list(self, device_list):
        """Persist the given list of devices."""

        logging.info("Storing (%d) devices." % (len(device_list)))

        logging.debug("About to clear our knowledge of existing knowledge.")
# TODO: Only remove actually-deleted devices.
        try:
            self.__device_registry.clear_ns(NS_DEVICE)
        except:
            logging.exception("Could not clear existing stored devices "
                              "(store).")
            raise

        i = 0
        for device in device_list:
            logging.debug("Writing device (%d)." % (i))

            try:
                self.store(device)
            except:
                logging.exception("Could not store device (%d) from list: %s" % 
                                  (i, device))
                raise

            i += 1

        logging.info("(%d) devices written." % (i))
    
    def store(self, device):
        """Persist the given list of devices."""

        logging.info("Storing device [%s]." % (device))

        driver = device.driver
    
        try:
            device_serialized = driver.__class__.convert_to_dict(device)
        except:
            logging.exception("Could not serialize device: %s" % (device))
            raise

        data = (driver.__module__, 
                driver.__class__.__name__, 
                device_serialized)

        try:
            self.__device_registry.set(NS_DEVICE, device.identifier, data, 
                                     comment=self.__comment, 
                                     value_type=T_COMPLEX)
        except:
            logging.exception("Could not store device: %s" % (device))
            raise

        logging.info("Device [%s] set." % (device))

    def retrieve_by_name(self, identifier):

        try:
            devices = self.retrieve_list()
        except:
            logging.exception("Could not retrieve list of devices.")
            raise
    
        for device in devices:
            if device.identifier == identifier:
                return device

        raise LookupError(identifier)
    
    def retrieve_list(self, state_filter=SF_AVAILABLE):
        """Retrieved stored devices. Omit any devices that are no longer 
        available.
        """

        logging.info("Retrieving stored devices.")

        try:
            stored = self.__device_registry.get(NS_DEVICE)
        except:
            logging.exception("Could not retrieve stored devices.")
            raise

        logging.debug("(%d) persisted devices found." % (len(stored)))

        devices = []
        unavailable = []
        num_restored = 0
        for identifier in stored.keys():
            try:
                device = self.__retrieve(identifier)
            except:
                logging.exception("Could not restore device with identifier "
                                  "[%s]. Device will be skipped." % 
                                  (identifier))
                continue
            
            logging.debug("Verifying device availability: %s" % (device))
            
            if device.driver.is_available(device):
                devices.append(device)
            else:
                unavailable.append(device)
                logging.warn("Device is no longer available: %s" % (device))
        
            num_restored += 1
        
        logging.info("(%d) devices restored." % (num_restored))
        
        raw_devices = (devices, unavailable)

        # Filter results based on desire.

        if state_filter == SF_AVAILABLE:
            final = raw_devices[0]
        elif state_filter == SF_MISSING:
            final = raw_devices[1]
        elif state_filter == SF_BOTH:
            final = raw_devices[0] + raw_devices[1]
        elif state_filter == SF_TUPLE:
            final = raw_devices

        return final

    def __retrieve(self, identifier):
        """Retrieved stored devices. Omit any devices that are no longer 
        available.
        """

        logging.info("Retrieving stored devices.")

        try:
            data = self.__device_registry.get(NS_DEVICE, identifier)
        except:
            logging.exception("Could not retrieve stored devices.")
            raise

        logging.debug("Restoring device with identifier [%s]" % (identifier))
        
        (module_name, class_name, device_serialized) = data
        
        full_class_name = ('%s.%s' % (module_name, class_name))
        
        try:
            driver_cls = load_class(full_class_name)
        except:
            logging.exception("Could not hot-import class [%s]." % 
                              (full_class_name))
            raise
        
        try:
            return driver_cls.convert_from_dict(device_serialized)
        except:
            logging.exception("Could not restore device object: %s" % 
                              (device_serialized))
            raise

