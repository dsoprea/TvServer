import json

from hashlib import sha1

#from rain_config import values
from big_id import BigId 

from interfaces.idictable import IDictable
from interfaces.iserializable import ISerializable
#from rain.common.modules import cf
from device.drivers import get_device_from_big_id, get_big_id_from_device

from logging import getLogger
logging = getLogger(__name__)

class TunerInfo(IDictable):
    """Tracks state of a specific tuner on a specific device."""

    def __init__(self, device, tuner_index):
        self.__device      = device
        self.__tuner_index = tuner_index
        self.__vchannel    = None

        # Note that this unique-ID is not embedded in serialization because
        # it's calculated based on two items that are.
        id_core = ("%s-%s" % (device.identifier, tuner_index))

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

        return { 'DeviceBigId': str(get_big_id_from_device(obj.__device)),
                 'TunerIndex':  obj.__tuner_index,
                 'VChannel':    obj.__vchannel }

    @staticmethod
    def convert_from_dict(data):
        """Restore an object from a dictionary."""

        try:
            device = get_device_from_big_id(BigId(data['DeviceBigId']))
        except:
            logging.exception("Could not restore device [%s]." %
                              (data['DeviceBigId']))
            raise

        tuner_info = TunerInfo(device, data['TunerIndex'])
        tuner_info.vchannel  = data['VChannel']

        return tuner_info

    @staticmethod
    def serialize(obj):
        """Reduce the given object to a string."""

        data = TunerInfo.convert_to_dict(obj)

        big_id = BigId(data['DeviceBigId'])
        
        # We want to have a properly wrapped ID (tuner info wrapping device 
        # info).
        
        serialized = ('%s:%s' % (data['TunerIndex'], 
                                 data['VChannel'] if data['VChannel'] \
                                                    is not None \
                                                  else ''))

        big_id.push(serialized)
        return str(big_id)

    @staticmethod
    def unserialize(data):
        """Restore an object from a string."""

        big_id = BigId(data)

        serialized = big_id.pop()
        (tuner_index, vchannel) = serialized.split(':')

        device = get_device_from_big_id(big_id)

        data = { 'DeviceIdent': device.identifier,
                 'TunerIndex':  int(tuner_index),
                 'VChannel':    int(vchannel) if vchannel else None}

        return TunerInfo.convert_from_dict(data)

    @staticmethod
    def build_from_id(id_):
        return TunerInfo.unserialize(id_)

    @property
    def identifier(self):
# TODO: Cache this until it changes.
        return self.__class__.serialize(self)

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

