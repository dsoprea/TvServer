import json

from rain_config import values

from rain.common.interfaces.idictable import IDictable
from rain.common.interfaces.iserializable import ISerializable
from rain.common.modules import cf

from logging import getLogger
logging = getLogger(__name__)

class TunerInfo(IDictable):
    """Tracks state of a specific tuner on a specific device."""

    def __init__(self, device, tuner_index):
        self.__device      = device
        self.__tuner_index = tuner_index
        self.__vchannel    = None
        self.__unique_id   = id(self)

    def __str__(self):
        return ('[%s]-%d @(%s)' % (self.device.identifier, self.tuner_index, 
                                   self.vchannel))

    def easy_capture_to_file(self, file_path, quality):
        """A utility function to record on this tuner."""

        try:
            return self.device.driver.capture_to_file(self, file_path, quality)
        except:
            logging.exception("Could not capture to file [%s]." % (file_path))
            raise

    def easy_set_vchannel(self, vchannel_scalar):
        """A utility function to set the vchannel on this tuner."""

        try:
            return self.device.driver.set_vchannel(self, vchannel_scalar)
        except:
            logging.exception("Could not set vchannel to (%s)." % 
                              (vchannel_scalar))
            raise

    @staticmethod
    def convert_to_dict(obj):
        """Reduce the given object to a dictionary."""

        return { 'DeviceIdent': obj.__device.identifier,
                 'TunerIndex':  obj.__tuner_index,
                 'VChannel':    obj.__vchannel,
                 'UniqueId':    obj.__unique_id }
    
    @staticmethod
    def convert_from_dict(data):
        """Restore an object from a dictionary."""

        try:
            device_storage = cf.get(values.C_DEV_STORAGE)
        except:
            logging.exception("Could not get device-storage component.")
            raise

        try:
            device = device_storage.retrieve_by_name(data['DeviceIdent'])
        except:
            logging.exception("Could not restore device [%s]." % 
                              (data['DeviceIdent']))
            raise

        tuner_info = TunerInfo(device, data['TunerIndex'])
        
        tuner_info.__vchannel  = data['VChannel']
        tuner_info.__unique_id = data['UniqueId']
    
        return tuner_info

    @staticmethod
    def serialize(obj):
        """Reduce the given object to a string."""

        return json.dumps(TunerInfo.convert_to_dict(obj))
    
    @staticmethod
    def unserialize(data):
        """Restore an object from a string."""

        return TunerInfo.convert_from_dict(json.loads(data))

    @property
    def unique_id(self):
        return self.__unique_id
    
    @property
    def device(self):
        return self.__device
    
    @property
    def tuner_index(self):
        return self.__tuner_index

    @property
    def vchannel(self):
        return self.__vchannel

    @vchannel.setter
    def vchannel(self, vchannel):
        self.__vchannel = vchannel

