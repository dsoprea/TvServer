from collections import OrderedDict

from logging import getLogger
logging = getLogger(__name__)

class PrimitiveChannelList(object):
    __list = {}
    __sort_function = None
    __cache = None

    def __init__(self, sort_function=None):
    
        self.__sort_function = sort_function if sort_function \
                                             else self.__default_sort_function

    def __default_sort_function(self, channels):
        """By default, sort by key and return in an OrderedDict."""
    
        sorted_keys = sorted(channels.keys())

        ordered_channels = OrderedDict()
        for key in sorted_keys:
            ordered_channels[key] = channels[key]

        return ordered_channels

    def add(self, designation, name, data=None):
        """Add a channel to the list.
        
        designation: Number/index/etc of channel.
        name: Name of channel.
        """

        self.__list[designation] = { 'Name': name,
                                     'Data': data,
                                   }

        self.__cache = None

    def remove(self, designation):
        """Remove a channel from the list."""

        del self.__list[designation]

        self.__cache = None

    @property
    def primitive_list(self):

        if self.__cache == None:
            try:
                self.__cache = self.__sort_function(self.__list)
            except:
                logging.exception("Could not get sorted list of channels.")
                raise
        
        return self.__cache

