import json

#from hashlib import sha1

import values

#from rain_config import values
from big_id import BigId 
from cf import get
from interfaces.idictable import IDictable
#from interfaces.iserializable import ISerializable
#from rain.common.modules import cf
from device.drivers import get_device_from_big_id, get_big_id_from_device

from logging import getLogger
logging = getLogger(__name__)


class TunerInfo(IDictable):
    """Tracks state of a specific tuner on a specific device."""

    def __init__(self, device, tuner_index):
        self.__device      = device
        self.__tuner_index = tuner_index
        self.__tune_data    = None

    def __str__(self):
        return ('[%s]-%d @(%s)' % (self.device.identifier, self.tuner_index,
                                   self.tune_data))

    def easy_capture_to_file(self, file_path, quality):
        """A utility function to record on this tuner."""

        try:
            return self.device.driver.capture_to_file(self, file_path, quality)
        except:
            logging.exception("Could not capture to file [%s]." % (file_path))
            raise

    def set_tune(self, param, host):
        """A utility function to initiate a tune."""

        try:
            return self.device.driver.set_tune(self, param, host)
        except:
            logging.exception("Could not tune with parameter [%s]." % (param))
            raise

    def is_allocated(self):
        tuner = get(values.C_DEV_TUNER)
        return tuner.get_status(self.__device, self.__tuner_index)

    @staticmethod
    def convert_to_dict(obj):
        """Reduce the given object to a dictionary."""

        return { 'DeviceBigId': repr(get_big_id_from_device(obj.__device)),
                 'TunerIndex': obj.__tuner_index,
                 'TuneData': obj.__tune_data }

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
        tuner_info.tune_data  = data['TuneData']

        return tuner_info

    @staticmethod
    def serialize(obj):
        """Reduce the given object to a string."""

        data = TunerInfo.convert_to_dict(obj)

        big_id = BigId(data['DeviceBigId'])
        
        # We want to have a properly wrapped ID (tuner info wrapping device 
        # info).
        
        serialized = ('%s:%s' % (data['TunerIndex'], 
                                 data['TuneData'] if data['TuneData'] \
                                                    is not None \
                                                  else ''))

        big_id.push(serialized)
        return repr(big_id)

    @staticmethod
    def unserialize(data):
        """Restore an object from a string."""

        big_id = BigId(data)

        serialized = big_id.pop()
        (tuner_index, tune_data) = serialized.split(':')

        # The remaining keys in big_id pertain to the device (we know because
        # of how we built it in serialize()).

        data = { 'DeviceBigId': big_id,
                 'TunerIndex': int(tuner_index),
                 'TuneData': int(tune_data) if tune_data else None}

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
    def tune_data(self):
        return self.__tune_data

    @tune_data.setter
    def tune_data(self, tune_data):
        self.__tune_data = tune_data

    def __hash__(self):
        return ('%s:%s:%s' % 
                (self.__device.identifier, 
                 self.__tuner_index, 
                 self.__tune_data if self.__tune_data is not None else ''))

    def __eq__(self, o):
        return (hash(self) == hash(o)) 

    def __ne__(self, o):
        return (hash(self) != hash(o))
