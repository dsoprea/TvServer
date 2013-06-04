from os.path import expanduser, isfile, basename
from datetime import datetime

from rain_config import constants

from rain.dvr.interfaces.device.channels.ichannellist import IChannelList
from rain.dvr.ui.snackwich_textfields import SnackwichTextFields
from rain.dvr.ui.exceptions import *
from rain.dvr.modules.device.channels.utility import parse_channels_conf
from rain.dvr.modules.device.channels.primitive_channel_list \
        import PrimitiveChannelList

from logging import getLogger
logging = getLogger(__name__)

class ChannelListChannelsConf(IChannelList):
    """Describes a list of channels."""

    __name                  = None
    __atsc_type             = None
    __channelsconf_filepath = None
    __list                  = None

    def __init__(self, name, atsc_type, channelsconf_filepath):
        self.__name                  = name
        self.__atsc_type             = atsc_type
        self.__channelsconf_filepath = channelsconf_filepath

        self.__load_channels()

    def __load_channels(self):
        try:
            channels = parse_channels_conf(self.__channelsconf_filepath)
        except:
            logging.exception("Could not load channels.conf data from file-"
                              "path [%s]." % (self.__channelsconf_filepath))
            raise

        channel_list = PrimitiveChannelList()

        for program_id, channel_info in channels.iteritems():
            channel_list.add(channel_info['ProgramId'], 
                             channel_info['Name'], 
                             { 'Frequency':  channel_info['Frequency'], 
                               'Modulation': channel_info['Modulation'],
                               'VideoId':    channel_info['VideoId'],
                               'AudioId':    channel_info['AudioId'],
                               'ProgramId':  channel_info['ProgramId'],
                             })

        self.__list = channel_list

    @staticmethod
    def __field_validator(values):
        (name, channelsconf_filepath, atsc_type) = values
        values = list(values)

        if not name or not channelsconf_filepath or not atsc_type:
            raise ValidationError("Please enter all values.")

        # Validate 'name'.

        name = name % { 'ChannelsConf': basename(channelsconf_filepath), 
                        'AtscType': atsc_type }
        values[0] = name

# TODO: Make sure that this name is unique among channel-lists.
# TODO: Prevent the same channels.conf file from being used in more than one channel-list.    
        # Validate 'channelsconf_filepath'.
    
        if not isfile(channelsconf_filepath):
            raise ValidationError("[%s] is not a valid file." % (channelsconf_filepath))

        # Validate 'atsc_type'.

        atsc_type = atsc_type.lower()
        found = None

        for one_adapter_value in constants.ADAPTER_TYPES:
            if atsc_type == one_adapter_value.lower():
                found = one_adapter_value
                break

        if not found:
            raise ValidationError("Please enter a valid type.")

        if found != values[2]:
            atsc_type = found
            values[2] = atsc_type

        # Return a [possibly updated] set of values.
        return values

    @staticmethod
    def __build_textfields():
        sw_textfields = SnackwichTextFields('ChannelsConf Fields', 
                                            ChannelListChannelsConf.__field_validator)

        #default_value = datetime.now().strftime("%Y%m%d-%H%M")
        default_value = '%(ChannelsConf)s %(AtscType)s'
        sw_textfields.add('List name', default_value)

        default_value = expanduser('~/channels.conf')
        sw_textfields.add('channels.conf location', default_value)

        types = '/'.join(constants.ADAPTER_TYPES)
        sw_textfields.add('Type (%s)' % (types))

        return sw_textfields

    @staticmethod
    def get_required_textfields():
        """Return a ITextFields object."""

        return ChannelListChannelsConf.__build_textfields()

    @staticmethod
    def factory(field_values):
        """Build an instance using a populated ITextFields object."""
        
        (name, channelsconf_filepath, atsc_type) = field_values
        
        try:
            return ChannelListChannelsConf(name,
                                           atsc_type, 
                                           channelsconf_filepath)
        except:
            logging.exception("Could not build ChannelListChannelsConf "
                              "object using ATSC-type [%s] and channels.conf "
                              "file-path [%s]." % 
                              (atsc_type, channelsconf_filepath))
            raise

    @property
    def list(self):
        """Return a PrimitiveChannelList object."""
    
        return self.__list

    @list.setter
    def list(self):
        """Set a PrimitiveChannelList object. This will only be used for those 
        IChannelList classes where channels_are_managed() returns True.
        """
    
        raise NotImplementedError()

    @staticmethod
    def convert_to_dict(obj):
        """Reduce the given object to a dictionary."""

        return { 'Name':                 obj.__name,
                 'AtscType':             obj.__atsc_type,
                 'ChannelsConfFilePath': obj.__channelsconf_filepath,
               }
    
    @staticmethod
    def convert_from_dict(data):
        """Restore an object from a dictionary."""

        try:
            return ChannelListChannelsConf(data['Name'],
                                           data['AtscType'], 
                                           data['ChannelsConfFilePath'])
        except:
            logging.exception("Could not build ChannelListChannelsConf "
                              "object using ATSC-type [%s] and channels.conf "
                              "file-path [%s]." % 
                              (data['AtscType'], data['ChannelsConfFilePath']))
            raise

    @property
    def name(self):
        """Return the name given to this channel-list."""
        
        return self.__name

    @property
    def requires_scan(self):
        """Returns boolean indicating whether this channel-list relies on a 
        channel-scan being performed.
        """

        return False

    @property
    def channels_are_managed(self):
        """Returns a boolean indicating whether the platform is keeping track
        of the channels, and should load the channels. Else, this class should
        do this internally.
        """
    
        return False

    def __str__(self):
        return ("ChannelListChannelsConf(NAME=\"%s\" TYPE=%s PATH=%s COUNT=%d)" % 
                (self.__name, self.__atsc_type, self.__channelsconf_filepath, 
                 len(self.__list.primitive_list)))

