from json import loads, dumps
from os.path import expanduser

#from rain_config import constants, channel_config, values

#from rain.common.modules import cf
from interfaces.device.itunerdriver import ITunerDriver
from device.device_network_attached import DeviceNetworkAttached
from device import DriverRequirementsError

#from rain.dvr.modules.device.channel_info import ChannelInfo
#from rain.dvr.modules.device.program_info import ProgramInfo
#from rain.dvr.modules.device.tuner_info   import TunerInfo

#from rain.dvr.modules.media.container_info import ContainerInfo
#from rain.dvr.modules.media.video_info     import VideoInfo
#from rain.dvr.modules.media.audio_info     import AudioInfo
#from rain.dvr.modules.media.subtitle_info  import SubtitleInfo
     
from logging import getLogger
logging = getLogger(__name__)

class DeviceHdHomeRun(DeviceNetworkAttached):
    """Represents a single available HDHomeRun device."""

    __ll_device = None
    __channellist = None
    
    def __init__(self, driver, ip, tuner_quantity, data=None, channellist=None):
        DeviceNetworkAttached.__init__(self, driver, ip, tuner_quantity, data)

        self.__ll_device   = data
        self.__channellist = channellist

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return ('DEV-HDHR %s(%s TUNERS=%d SN=%s)' % (self.driver.__class__.__name__, 
                                           self.__ll_device.nice_ip, 
                                           self.__ll_device.tuner_count, 
                                           self.__ll_device.nice_device_id))

    @property
    def supported_channelliststypes(self):
        """Return the support channel-list classes that we support for tuning.
        """
        
        return [channel_config.LT_SCAN]

    @property
    def channellist(self):
        """Return an instance of the IChannelList that we currently tune with.
        """
    
        raise self.__channellist

    @channellist.setter
    def channellist(self, channellist):
        """Set a new instance of an IChannelList to tune with."""

        self.__channellist = channellist

class DriverHdHomeRun(ITunerDriver):
    """Represents an interface to a particular class of TV tuner."""

    HdhrUtility                      = None
    HdhrDeviceQuery                  = None
    HdhrVideo                        = None
    TYPE_hdhomerun_discover_device_t = None
    get_hdhr                         = None

    @staticmethod
    def __init_so():
    
        try:
            from pyhdhomerun.adapter import HdhrUtility, HdhrDeviceQuery, HdhrVideo
            from pyhdhomerun.types import TYPE_hdhomerun_discover_device_t
            from pyhdhomerun.hdhr import get_hdhr
        except Exception as e:
            raise DriverRequirementsError("Could not load PyHdHomeRun: %s" % 
                                          (str(e)), 
                                          DriverHdHomeRun())

        DriverHdHomeRun.HdhrUtility = HdhrUtility
        DriverHdHomeRun.HdhrDeviceQuery = HdhrDeviceQuery
        DriverHdHomeRun.HdhrVideo = HdhrVideo
        DriverHdHomeRun.TYPE_hdhomerun_discover_device_t = TYPE_hdhomerun_discover_device_t
        DriverHdHomeRun.get_hdhr = get_hdhr

    def __init__(self):

        # In order for the configuration tool to not crash due to dependency
        # problems with drivers, such crashing needs to be isolated to here.

        DriverHdHomeRun.__init_so()

    def enumerate_devices(self):
        """List available devices."""

        try:
            devices = self.HdhrUtility.discover_find_devices_custom()
        except:
            logging.exception("There was an exception while trying to discover "
                             "HdHomeRun devices.")
            raise

        formal = []
        for device in devices:
            try:
                device = DeviceHdHomeRun(self, device.nice_ip, 
                                         device.tuner_count, device)

                formal.append(device)
            except:
                logging.exception("Could not formalize found device.")
                raise

        return formal

    @staticmethod
    def convert_to_dict(device):
        """Reduce the given device to a dictionary."""

        channellist_name = device.channellist.name if device.channellist \
                                                   else None

        return { 'IpAddr':      device.junk_data.ip_addr,
                 'DeviceType':  device.junk_data.device_type,
                 'DeviceId':    device.junk_data.device_id,
                 'TunerCount':  device.junk_data.tuner_count,
                 'ChannelList': channellist_name,
               }
    
    @staticmethod
    def convert_from_dict(data):
        """Restore a device from a dictionary."""

        DriverHdHomeRun.__init_so()

        try:
            channel_storage = cf.get(values.C_CHANNEL_STORAGE)
        except:
            logging.exception("Could not get channel-storage component.")
            raise

        channellist = data['ChannelList']

        if channellist:
            try:
                channellist = channel_storage.get_channellist(channellist)
            except:
                logging.exception("Could not restore DriverDeviceFile device with "
                                  "broken channel-list: %s" % (data))
                raise
    
        driver = DriverHdHomeRun()
    
        try:
            device = DriverHdHomeRun.TYPE_hdhomerun_discover_device_t()
            device.ip_addr     = data['IpAddr']
            device.device_type = data['DeviceType']
            device.device_id   = data['DeviceId']
            device.tuner_count = data['TunerCount']

            device.channellist = channellist
        except:
            logging.exception("Could not rebuild lower-level device object.")
            raise
    
        try:
            return DeviceHdHomeRun(driver, device.nice_ip, device.tuner_count, 
                                   device)
        except:
            logging.exception("Could not rebuild local device object.")
            raise
            
    def is_available(self, device):
        """Check if the given device is still available."""

# TODO: Ensure that the HdhrUtility call actually checks at the specific IP.    
        try:
            found = self.HdhrUtility.discover_find_devices_custom(device.address)
        except:
            logging.exception("There was an exception while trying to check the"
                             " availability of HdHomeRun device at [%s]." %
                             (device.address))
            raise

        return bool(found)

    def __get_hd(self, tuner):

        # Address the first tuner on the given device.
        device_str = ("%s-%d" % (tuner.device.address, tuner.tuner_index))

        try:
            return self.HdhrUtility.device_create_from_str(device_str)
        except:
            logging.exception("Could not create device entity from string "
                              "[%s]." % (device_str))
            raise

    def iterate_channels_start(self, device, tuner_index, channel_map):
        """Establish the initial state information for a channel-scan. As 
        opposed to the generator function, this allows the caller to stash the
        state value and each, next, successive channel at some unspecified time
        in the future. Returns a blackbox state object.
        """

        logging.info("Initializing channel-scan state.")

        tuner = TunerInfo(device, tuner_index)
        hd = self.__get_hd(tuner)
        device_query = self.HdhrDeviceQuery(hd)

        scan_info = device_query.iterate_channels_start(channel_map)

        return (device_query, scan_info)

    def iterate_channels_next(self, state):
        """Take the object returned by iterate_channels_start and scan the next
        channel. Returns False if done, None if channel is to be skipped, or
        "(progress_int, ChannelInfo, <ProgramInfo[]>)" if channel successfully 
        locked.
        """

        (device_query, scan_info) = state

        logging.debug("Proceeding to next in channel-scan.  PROGRESS= "
                      "(%d)/(%s)" % (scan_info['current'], scan_info['count']))

        try:
            result = device_query.iterate_channels_next(scan_info)
        except:
            logging.exception("Exception while iterating the channel during a "
                              "scan.")
            raise
        
        # Scan is finished.
        if result == False:
            logging.error("Channel-scan has finished (driverhdhomerun).")
            return (False,)
        
        progress = int(float(scan_info['current']) / float(scan_info['count']) * 100.0)

        # Channel could not be locked or was empty of programs.
        if result == None or not result.programs:
            logging.debug("No programs found.")
            return (progress,)

        channel_data = result

        raw_id = channel_data.channel_str
        channel_id = int(raw_id[raw_id.find(':') + 1:])
        channel_info = ChannelInfo(channel_id, 
                                   channel_data.channel_str, 
                                   int(channel_data.frequency)
                                  )

        programs = []
        i = 0
        for i in xrange(channel_data.program_count):
            program_raw = channel_data.programs[i]

            #define HDHOMERUN_CHANNELSCAN_PROGRAM_NORMAL 0
            #define HDHOMERUN_CHANNELSCAN_PROGRAM_NODATA 1
            #define HDHOMERUN_CHANNELSCAN_PROGRAM_CONTROL 2
            #define HDHOMERUN_CHANNELSCAN_PROGRAM_ENCRYPTED 3
            if program_raw.type not in [0, 3]:
                continue
# TODO: Make sure we only store values available from any ATSC tuner.

            program_info = ProgramInfo(channel_id, 
                                       int(program_raw.virtual_major), 
                                       int(program_raw.program_number), 
                                       int(program_raw.virtual_major), 
                                       int(program_raw.virtual_minor), 
                                       program_raw.name,
                                       i,
                                       int(program_raw.type),
                                      )

            programs.append(program_info)
            i += 1

        if not programs:
            # It turns out that there were no usable programs.
            logging.debug("No programs were actually found.")
            return (progress,)

        logging.debug("(%d) acceptable programs found on this channel." % 
                      (len(programs)))

        return (progress, channel_info, programs)

    def capture_to_file(self, tuner, file_path, quality):
        """Start streaming and storing directly to a file. Used primarily for
        testing. The 'quality' parameter indicates what level of quality to
        return if there's a choice. This is mostly for bandwidth conservation,
        if there's an opportunity.
        """
    
        hd = self.__get_hd(tuner)

        try:
            return self.HdhrVideo(hd).stream_to_file(file_path)
        except:
            logging.exception("Could not capture to file [%s]." % (file_path))
            raise

#    def check_tuning_status(self, tuner):
#        """Determine if the channel is still tuned properly."""
#    
#        pass

    def set_vchannel(self, tuner, vchannel_scalar=None):
        """Set the vchannel on the given tuner to the given scalar."""

# TODO: Finish support for vchannel_scalar being None.    
        hd = self.__get_hd(tuner)

        try:
            self.HdhrDeviceQuery(hd).set_tuner_vchannel(vchannel_scalar)
        except:
            logging.exception("Could not set vchannel to (%d)." % 
                              (vchannel_scalar))
            raise

        tuner.vchannel = vchannel_scalar

    def generate_panels(self, panel_name_generator, notice_box, for_device):
        """If this driver needs specific global configuration settings in order 
        to tune or whatnot, return a list of additional panels. If any 
        panel expressions do not have a '_next' component, it will be defaulted
        to whatever 'return_to_panel' is, above. Any data that is to be stored
        should be set on persisted_data (a dictionary).
        """

        return None

    @property
    def name(self):
        """Returns a nice, human-readable name for this driver."""
        
        return 'HDHomeRun'

    @property
    def description(self):
        """Returns a string that describes the type of device that we handle.
        """
        
        return """HDHomeRun network-attached tuners."""

    @property
    def transport_info(self):
        """Returns a description of the media stream."""

# TODO: Map this from the stream.

        raise NotImplementedError()
#        video_info = VideoInfo(constants.M_VID_MPEG2)
#        audio_info_english = AudioInfo(constants.LANG_ENGLISH, constants.M_AUD_AC3)
#        audio_info_spanish = AudioInfo(constants.LANG_SPANISH, constants.M_AUD_AC3)
#        subtitle_info = SubtitleInfo(constants.LANG_ENGLISH, '<abc>')
#
#        container_name = ContainerInfo(                 \
#                            constants.M_CHANNEL_MPEGTS, \
#                            { 0: video_info },          \
#                            { 1: video_info_english,    \
#                              2: video_info_spanish     \
#                            },                          \
#                            { 3: subtitle_info }        \
#                           )
#        
#        return container_name

    @property
    def supports_channelscan(self):
        """Returns a boolean expressing whether a channel-scan is both 
        supported and required. A driver that doesn't support a manual channel-
        scan must have some other method of determining channels, such as 
        having been given a channels.conf file.
        """
        
        return True

