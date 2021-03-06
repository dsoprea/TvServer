from tv_server.interfaces.device.itunerdriver import ITunerDriver, \
                                                     TD_TYPE_VCHANNEL
from tv_server.device.device_network_attached import DeviceNetworkAttached
from tv_server.device import DriverRequirementsError

from logging import getLogger
logging = getLogger(__name__)

class DeviceHdHomeRun(DeviceNetworkAttached):
    """Represents a single available HDHomeRun device."""

    __ll_device = None
    __channellist = None
    
    def __init__(self, driver, ip, tuner_quantity, data=None, channellist=None):
        super(DeviceHdHomeRun, self).__init__(driver, ip, tuner_quantity, data)

        self.__driver = driver
        self.__ip = ip
        self.__ll_device   = data
        self.__channellist = channellist

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return ('DEV-HDHR %s(%s TUNERS=%d SN=%s)' % 
                (self.driver.__class__.__name__, 
                 self.__ll_device.nice_ip, 
                 self.__ll_device.tuner_count, 
                 self.__ll_device.nice_device_id))

    @property
    def driver(self):
        """Returns the driver that represents us."""

        return self.__driver

    @property
    def identifier(self):
        """Return an adapter-filepath."""

        return self.address

    @property
    def address(self):
        """Returns the DVB file-path."""

        return self.__ip

    @property
    def tuner_quantity(self):
        """Returns the number of tuners available on the device."""

        return self.__ll_device.tuner_count

    def __hash__(self):
        return hash(self.identifier)

    def __eq__(self, o):
        return (hash(self) == hash(o)) 

    def __ne__(self, o):
        return (hash(self) != hash(o))


class DriverHdHomeRun(ITunerDriver):
    """Represents an interface to a particular class of TV tuner."""

    HdhrUtility                      = None
    HdhrDeviceQuery                  = None
    HdhrVideo                        = None
    TYPE_hdhomerun_discover_device_t = None
    library_instance                 = None

    @staticmethod
    def __init_so():
    
        try:
            from pyhdhomerun.adapter import HdhrUtility, HdhrDeviceQuery, HdhrVideo
            from pyhdhomerun.types import TYPE_hdhomerun_discover_device_t
            import pyhdhomerun.hdhr
        except Exception as e:
            raise DriverRequirementsError("Could not load PyHdHomeRun: %s" % 
                                          (str(e)))

        DriverHdHomeRun.HdhrUtility = HdhrUtility
        DriverHdHomeRun.HdhrDeviceQuery = HdhrDeviceQuery
        DriverHdHomeRun.HdhrVideo = HdhrVideo
        DriverHdHomeRun.TYPE_hdhomerun_discover_device_t = TYPE_hdhomerun_discover_device_t
        DriverHdHomeRun.library_instance = pyhdhomerun.hdhr.library

    def __init__(self):

        # In order for the configuration tool to not crash due to dependency
        # problems with drivers, such crashing needs to be isolated to here.

        DriverHdHomeRun.__init_so()

    def __build_from_enumerated(self, enumerated_device):
        try:
            return DeviceHdHomeRun(self, 
                                   enumerated_device.nice_ip, 
                                   enumerated_device.tuner_count, 
                                   enumerated_device)

        except:
            logging.exception("Could not formalize found device [%s]." % 
                              (enumerated_device))
            raise

    def __enumerate_devices_internal(self, ip=None):
        """List available devices."""

        try:
            found = self.HdhrUtility.discover_find_devices_custom(ip)
        except:
            logging.exception("There was an exception while trying to discover "
                             "HdHomeRun devices.")
            raise

        devices = []
        for found_device in found:
            device = self.__build_from_enumerated(found_device)
            devices.append(device)

        return devices

    def build_from_id(self, id_):
        """Our id is the IP of the adapter."""

        found = self.__enumerate_devices_internal(id_)
        if not found:
            raise Exception("Device with IP [%s] for rebuild was not found." % 
                            (id_))

        return found[0]

    def enumerate_devices(self):
        return self.__enumerate_devices_internal()

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

# TODO: Finish.
#    def check_tuning_status(self, tuner):
#        """Determine if the channel is still tuned properly."""
#    
#        pass

    def set_tune(self, tuner, vchannel_scalar, target):
        """Set the vchannel on the given tuner to the given scalar."""

        hd = self.__get_hd(tuner)

        (host, ip) = target
        target_uri = ('rtp://%s:%d' % (host, ip))

        query = self.HdhrDeviceQuery(hd)

        try:
            query.set_tuner_vchannel(vchannel_scalar)
            query.set_tuner_target(target_uri)
        except:
            logging.exception("Could not tune with tuner [%s] to [%s] with a "
                              "target of [%s]." % 
                              (tuner, vchannel_scalar, target_uri))
            raise

        tuner.vchannel = vchannel_scalar

    def clear_tune(self, tuner):
        """Set the vchannel on the given tuner to the given scalar."""

        hd = self.__get_hd(tuner)

        try:
            self.HdhrDeviceQuery(hd).set_tuner_target(None)
        except:
            logging.exception("Could not clear tune on HDHR for tuner: %s" % 
                              (tuner))
            raise

        tuner.vchannel = None

    @property
    def name(self):
        """Returns a nice, human-readable name for this driver."""
        
        return 'HDHomeRun'

    @property
    def description(self):
        """Returns a string that describes the type of device that we handle.
        """
        
        return """HDHomeRun network-attached tuners. Tunes using a v-channel."""

    @property
    def tuner_data_type(self):
        """Returns one of the TD_TYPE_* values (above)."""

        return TD_TYPE_VCHANNEL 

    @property
    def stream_mimetype(self):
        return "video/mpegts"

