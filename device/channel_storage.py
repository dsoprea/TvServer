import json

from rain_config import values, channel_config
from rain_config.config_namespaces import NS_CHANNELLIST
from rain_config.values import CONF_CHANNELS

from rain.common.interfaces.iconfigstore import T_COMPLEX
from rain.common.modules import cf
from rain.common.modules.utility import get_pp_json
from rain.dvr.interfaces.device.ichannelstorage import IChannelStorage

from logging import getLogger
logging = getLogger(__name__)

# TODO: Clean this up. It might display all of the methods at the top of execution.
def d_debug(f):
#    logging.info("=== %s ===" % (f.__name__))
    return f
    
class ChannelStorage(IChannelStorage):

    __channels_registry = None
    __device_store      = None

    comment_channel        = None
    comment_channellist    = None

    def __init__(self):
        config_manager = cf.get(values.C_CONFIG)

        self.__channels_registry = config_manager.get_registry(CONF_CHANNELS)

        try:
            self.__device_storage = cf.get(values.C_DEV_STORAGE)
        except:
            logging.exception("Could not get device-storage component.")
            raise
        
        self.comment_channel        = self.__get_comment('channel')
        self.comment_channellist    = self.__get_comment('channellist')
        
        self.__channels_registry.create_tables()

    def __get_comment(self, key):
    
        try:
            dbcomments = cf.get(values.C_TEXT_DBCOMMENTS)
            return dbcomments.get(['Device', 'Channels'], key)
        except Exception as e:
            message = ("Could not find comment text for channel configurable "
                       "with namespace [%s], and key [%s]: %s" % (ns, key, e))
        
            logging.error(message)
            raise Exception(message)

    @d_debug
    def get_channellist_types(self):
        """Return a dictionary of type names to type classes."""

        logging.info("Retrieving list of channel-list types.")

        cl_dict = {}
        for cl_type in channel_config.cl_get_types():
            description = channel_config.cl_get_description(cl_type)
            cls         = channel_config.cl_get_class(cl_type)
            
            cl_dict[description] = cls

        return cl_dict

    @d_debug
    def store_channellist(self, channellist):
        """Store or replace the given IChannelList."""

        logging.info("Storing channel-list [%s]." % (channellist))

        channellist_cls = channellist.__class__
        channellist_data = channellist_cls.convert_to_dict(channellist)

        cl_type = channel_config.cl_get_type_from_class(channellist_cls)
        channellist_info = (cl_type, channellist_data)

        try:
            self.__channels_registry.set(NS_CHANNELLIST, 
                                       channellist.name, 
                                       channellist_info, 
                                       self.comment_channellist, 
                                       T_COMPLEX)
        except:
            logging.exception("Could not retrieve stored channel-lists.")
            raise

    @d_debug
    def remove_channellist(self, name):
        """Remove the channel-list from storage."""

        logging.info("Removing channel-list with name [%s]." % (name))

        try:
            self.__channels_registry.clear(NS_CHANNELLIST, name)
        except:
            logging.exception("Could not clear configured channel-list.")
            raise

    @d_debug
    def get_channellist(self, name):

        logging.info("Retrieving channel-list with name [%s]." % (name))

        try:
            channellist_info = self.__channels_registry.get(NS_CHANNELLIST, name)
        except:
            logging.exception("Could not retrieve stored channel-lists.")
            raise

        (cl_type, data) = channellist_info
        
        cl_cls = channel_config.cl_get_class(cl_type)

        if not cl_cls:
            raise Exception("Could not find channel-list class for type "
                            "[%s]." % (cl_type))

        try:
            return cl_cls.convert_from_dict(data)
        except:
            logging.exception("Could not reconstruct channel-list using "
                              "class [%s] and data [%s]." % 
                              (cl_cls, data))
            raise

    @d_debug
    def get_channellists(self):
        """Get a list of the channel-lists that have been stored."""

        logging.info("Retrieving channel-lists.")

        try:
            raw_channellists = self.__channels_registry.get(NS_CHANNELLIST)
        except:
            logging.exception("Could not retrieve stored channel-lists.")
            raise

        channellists = []
        for name in raw_channellists.keys():
            channellists.append(self.get_channellist(name))

        return channellists

    @d_debug
    def set_channellist_mapping(self, device, channellist):
        """Assign the given channel-list to the given device."""

        logging.info("Assigning channel-list [%s] to device [%s]." % 
                     (channellist, device))

        device.channellist = channellist

        try:
            self.__device_storage.store(device)
        except:
            logging.exception("Could not store device [%s] with updated "
                              "channel-list [%s]." % (device, channellist))
            raise

    @d_debug
    def clear_channellist_mapping_by_device(self, device):
        """Clear the channel-list mapping for the given device."""

        self.set_channellist_mapping(device, None)

    @d_debug
    def clear_channellist_mapping_by_channellist(self, channellist):
        """Clear the channel-list mapping for any device mapped to the given
        channel-list.
        """

        logging.info("Clearing all mappings for channel-list [%s]." % 
                     (channellist))

        try:
            devices = self.__device_storage.retrieve_list()
        except:
            logging.exception("Could not retrieve list of devices in order to "
                              "clear mappings for channel-list [%s]." % 
                              (channellist))
            raise

        for device in devices:
            self.clear_channellist_mapping_by_device(device)


