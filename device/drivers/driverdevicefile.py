import sha
import re
import subprocess
import multiprocessing
import Queue

from hashlib import sha1

from json import loads, dumps
from os.path import expanduser, isfile, isdir, dirname, exists
from os import listdir, stat, minor, major, environ, kill
from fnmatch import fnmatch
from platform import system
from signal import SIGALRM

from pyzap.calls import c_azap_tune_silent
from pyzap.types import *
from pyzap.constants import modulation

#from rain_config import constants, values, channel_config, \
#                                routine_close_priority

from interfaces.device.itunerdriver import ITunerDriver
from interfaces.device.itunerdevice import ITunerDevice
from interfaces.device.ituner import *
from device.device_network_attached import DeviceNetworkAttached
from device.tuner_device_common import TunerDeviceCommon
from device import DriverRequirementsError, DriverConfigurationError


#from mediaconsole.modules.media.container_info import ContainerInfo
#from mediaconsole.modules.media.video_info     import VideoInfo
#from mediaconsole.modules.media.audio_info     import AudioInfo
#from mediaconsole.modules.media.subtitle_info  import SubtitleInfo

from logging import getLogger
logging = getLogger(__name__)

(DEVICE_DEMUX, DEVICE_DVR, DEVICE_FRONTEND) = (0, 1, 2)

MT_ERROR     = 'error'
MT_CANCELLED = 'cancelled'
MT_STATUS    = 'status'

TS_1_INITIAL   = 'initial'
TS_2_TRYING    = 'trying'
TS_3_LOCKED    = 'locked'
TS_4_CANCELLED = 'done'

class DeviceFileDevice(TunerDeviceCommon, ITunerDevice):
    """Represents a device enumerated via DriverDeviceFile."""

    __driver      = None
    __adapter     = None
    __device_sets = None
    __tuner_count = None
    __sn          = None
    __channellist = None
    __atsc_type   = None

    def __init__(self, driver, adapter, adapter_index, device_sets, sn,
                 channellist=None, atsc_type=None):
        self.__driver        = driver
        self.__adapter       = adapter
        self.__adapter_index = adapter_index
        self.__device_sets   = device_sets
        self.__sn            = sn
        self.__channellist   = channellist
        self.__atsc_type     = atsc_type

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        channellist_name = self.__channellist.name if self.__channellist \
                                                   else None

        return ('DEV-FILE %s(%s TUNERS=%d SN=%s CHANNELS=[%s] TYPE=%s STATE=%d)' %
                (self.__driver.__class__.__name__,
                 self.__adapter,
                 len(self.__device_sets),
                 self.__sn[0:5],
                 channellist_name,
                 self.__atsc_type,
                 int(self.driver.is_available(self))))

    @property
    def driver(self):
        """Returns the driver that represents us."""

        return self.__driver

    @property
    def identifier(self):
        """Return a unique identifer for this device."""

        unique_string = ('%s(%s,%s)' % (self.__driver.name, self.__adapter,
                                        self.__sn[0:5]))

        return sha1(unique_string).hexdigest()

    @property
    def address(self):
        """Returns the network address, memory location, etc.., where this
        device is listening.
        """

        return self.__adapter

    @property
    def junk_data(self):
        """Returns an object of an unspecified type that the driver knows how
        to interpret. Used for implementation-specific data to be passed from
        the device to the driver.
        """

        return { 'DeviceSets':   self.__device_sets,
                 'AtscType':     self.__atsc_type,
                 'Adapter':      self.__adapter,
                 'Sn':           self.__sn,
               }

    @property
    def tuner_quantity(self):
        """Returns the number of tuners available on the device."""

        return len(self.__device_sets)

    @property
    def atsc_type(self):
        return self.__atsc_type

    @atsc_type.setter
    def atsc_type(self, value):
        self.__atsc_type = value

    @property
    def supported_channelliststypes(self):
        """Return the support channel-list classes that we support for tuning.
        """

        return [channel_config.LT_CHANNELSCONF]

    @property
    def channellist(self):
        """Return an instance of the IChannelList that we currently tune with.
        """

        return self.__channellist

    @channellist.setter
    def channellist(self, channellist):
        """Set a new instance of an IChannelList to tune with."""

        self.__channellist = channellist

    @property
    def adapter_index(self):
        return self.__adapter_index

    @adapter_index.setter
    def adapter_index(self, value):
        self.__adapter_index = value

class _ExecuteError(Exception):
    """There was a failure executing an external command."""

    def __init__(self, retval):
        Exception.__init__(self, "Command failed with (%d)." % (retval))

# TODO: Update the channels-conf references for our channel-list concept.

class _TuneChannel(multiprocessing.Process):#, ManagedRoutine):
    """The multiprocessing process that invokes the external utilities to tune
    channels.
    """

    __tuner                 = None
    __msg_queue             = None
    __cancel_event          = None

    def __init__(self, tuner, msg_queue):
        name = ('TuneChannel-%s' % (tuner.unique_id))

        multiprocessing.Process.__init__(self, name=name)
        #ManagedRoutine.__init__(self, name, routine_close_priority.P_TUNING_THREAD)

        self.__tuner        = tuner
        self.__msg_queue    = msg_queue
        self.__cancel_event = multiprocessing.Event()

    def run(self):

        logging.info("Starting tuning process for tuner [%s] on PID (%s)." %
                     (self.__tuner, self.pid))

        try:
            self.__tune()
        except Exception as e:
            self.__msg_queue.put((MT_ERROR, "There was an exception: %s" % (str(e))))
            logging.exception("There was an exception while tuning. Tuning "
                              "cancelled.")

        logging.info("Tuning process for tuner [%s] is stopping."%
                     (self.__tuner))

        self.__msg_queue.put((MT_CANCELLED, None))

    def __tune(self):
        """Tune the channel. This is a blocking call. Note that if the
        v-channel is not valid, there will be an exception immediately, but
        that if there is a tuning error, the error will be emitted to the
        queue.
        """

        tuner = self.__tuner
        device = self.__tuner.device
        junk_data = device.junk_data

        device_sets = junk_data['DeviceSets']

        if tuner.tuner_index >= len(device_sets):
            raise IndexError("Tuner with index (%d) is not valid for device "
                             "[%s]." % (tuner.tuner_index, device))

        descriptor = TUNER_DESCRIPTOR()
        descriptor.adapter  = device.adapter_index
        descriptor.frontend = device_sets[tuner.tuner_index][DEVICE_FRONTEND]
        descriptor.demux    = device_sets[tuner.tuner_index][DEVICE_DEMUX]

        # Get data from row in channels.conf .

        channel_info = device.channellist.list.primitive_list[tuner.vchannel]
        channel_data = channel_info['Data']

        name           = channel_info['Name']
        frequency      = channel_data['Frequency']
        modulation_raw = channel_data['Modulation']
        video_id       = channel_data['VideoId']
        audio_id       = channel_data['AudioId']
        program_id     = channel_data['ProgramId']

        # Map from the modulation in the channels.conf to the modulation
        # required by PyZap.

        file_to_pyzap_mod = { 'QPSK':   'QPSK',
	                          'QAM16':  'QAM_16',
	                          'QAM32':  'QAM_32',
	                          'QAM64':  'QAM_64',
	                          'QAM128': 'QAM_128',
	                          'QAM256': 'QAM_256',
	                          '8VSB':   'VSB_8',
	                          '16VSB':  'VSB_16' }

        if modulation_raw not in file_to_pyzap_mod:
            raise KeyError("Could not convert channels.conf modulation [%s] "
                           "to PyZap modulation." % (modulation_raw))

        pyzap_modulation_raw = file_to_pyzap_mod[modulation_raw]

        try:
            pyzap_modulation = modulation(pyzap_modulation_raw)
        except:
            logging.exception("Could not produce final module for PyZap "
                              "modulation string [%s] (original [%s])." %
                              (pyzap_modulation_raw, modulation))
            raise

        atsc_tune_info = ATSC_TUNE_INFO()

        atsc_tune_info.frequency  = int(frequency)
        atsc_tune_info.modulation = int(pyzap_modulation)
        atsc_tune_info.vpid       = int(video_id)
        atsc_tune_info.apid       = int(audio_id)

        # Do the tune. This will continue until the driver emits a SIGALRM,
        # which will break the loop in ZapLib.

        def status_receiver(status, signal, snr, ber, uncorrected_blocks, \
                            is_locked):
            try:
                status_package = (status, signal, snr, ber,
                                  uncorrected_blocks, is_locked)

                self.__msg_queue.put((MT_STATUS, status_package))

                return 1
            except KeyboardInterrupt:
                return 0

#            print('%X' % status)
#            print('%X' % signal)
#            print('%X' % snr)
#            print('%X' % ber)
#            print('%X' % uncorrected_blocks)
#            print('%X' % is_locked)

        try:
            c_azap_tune_silent(descriptor, atsc_tune_info, 1,
                               STATUS_RECEIVER_CB(status_receiver))
        except Exception as e:
            logging.exception("There was an exception while doing the "
                              "low-level tuning.")
            raise

    def cancel(self):
        """Stop tuning the channel. Called by original process. This call must
        block until the thread has finished.
        """

        logging.info("Cancelling tune on [%s]." % (self.__tuner))

        self.__cancel_event.set()

        logging.info("Sending SIGALRM to PID (%d) to cancel tuning." % (self.pid))

        # We wrap the kill in a try-catch since we'll get an OSError if the
        # process is already dead.

        try:
            kill(self.pid, SIGALRM)
        except:
            logging.error("Tuning process with PID (%d) could not be "
                          "cancelled (may already be dead)." % (self.pid))

        # We wrap the join in a try-catch just in case it's an exception to
        # join a thread that might already not be alive.

        try:
            self.join()
        except:
            pass

        logging.info("Cancel of tune on tuner [%s] complete." % (self.__tuner))

    def is_cancelled(self):
        return self.__cancel_set.is_set()

class DriverDeviceFile(ITunerDriver):
    """Represents an interface to a device represented by a
    /dev/dvb/adapter<n> device.
    """

    __atsc_type             = None

    __tuned                 = {}

    __device_search_path = '/dev/dvb'

    def enumerate_devices(self):
        """List available devices."""

        try:
            adapters = self.__get_adapters()
        except Exception as e:
            logging.exception("Devices error: %s" % (str(e)))
            raise

        devices = []
        for adapter in adapters:
            (adapter_filepath, adapter_index) = adapter

# If the SN has been given, check it against what we can calculate, here, and
# tell the system to ignore the device if the SNs don't match (the device is
# not present).
            try:
                device_sets = self.__get_tuners_on_adapter(adapter_filepath)
            except:
                logging.exception("Could not retrieve tuners for [%s]." %
                                  (adapter_filepath))
                raise

            try:
                sn = self.__build_sn(device_sets, adapter_filepath)
            except:
                logging.exception("Could not build SN for device [%s]." %
                                  (adapter_filepath))
                raise

            try:
                device = DriverDeviceFile.__build_device(self,
                                                         adapter_filepath,
                                                         adapter_index,
                                                         sn,
                                                         device_sets)
            except:
                logging.exception("Could not build device for adapter [%s] "
                                  "during enumeration." % (adapter_filepath))
                raise

            devices.append(device)

        return devices

    @staticmethod
    def __build_device(driver, adapter, adapter_index, sn, device_sets,
                       channellist=None, atsc_type=None):
        """Some of these parameters really can't be omitted. However, if we're
        enumerating devices, the users won't be able to select values for them
        until we can present the detected devices.
        """

        logging.debug("Building device object for adapter [%s]." % (adapter))

        try:
            return DeviceFileDevice(driver,
                                     adapter,
                                     adapter_index,
                                     device_sets,
                                     sn,
                                     channellist,
                                     atsc_type
                                    )
        except:
            logging.exception("Could not build device for device-path "
                              "[%s]." % (adapter))
            raise

    def __build_device_filepath(self, adapter_filepath, index, _type):
        if _type == DEVICE_DEMUX:
            file_prefix = 'demux'
        elif _type == DEVICE_DVR:
            file_prefix = 'dvr'
        elif _type == DEVICE_FRONTEND:
            file_prefix = 'frontend'

        return ("%s/%s%d" % (adapter_filepath, file_prefix, index))

    def __build_sn(self, device_sets, adapter):
        """Build the SN for the device from the SNs from each of the tuners,
        represented by their individual dvr<n> devices.
        """

        serials = ''
        for device_set in device_sets:
            tuner_file_path = self.__build_device_filepath(
                                adapter,
                                device_set[DEVICE_DVR],
                                DEVICE_DVR)

            s = stat(tuner_file_path)
            dev_id_string = ('%s:%s' % (major(s.st_rdev), minor(s.st_rdev)))
            device_info_root = ('/sys/dev/char/%s' % (dev_id_string))
            sn_filepath = ('%s/device/serial' % (device_info_root))

#            logging.debug("Device info root is [%s]." % (device_info_root))

            if not isfile(sn_filepath):
                message = ('Can not find serial at [%s] for tuner [%s].' %
                           (sn_filepath, tuner_file_path))

                logging.error(message)
                raise Exception(message)

            try:
                with open(sn_filepath) as f:
                    sn = f.read()
            except:
                message = ("Could not read SN from [%s]." % (sn_filepath))

                logging.error(message)
                raise

#            logging.debug("Tuner [%s] SN: %s" % (tuner_file_path, sn))

            serials += sn

        return sha.new(serials).hexdigest()

    @staticmethod
    def convert_to_dict(device):
        """Reduce the given device to a dictionary."""

        logging.debug("Serializing device to dictionary.")

        channellist_name = device.channellist.name if device.channellist \
                                                   else None
# TODO: Move the data out of the junk_data dict.
        return { 'DeviceSets':   device.junk_data['DeviceSets'],
                 'AtscType':     device.junk_data['AtscType'],
                 'Adapter':      device.junk_data['Adapter'],
                 'Sn':           device.junk_data['Sn'],
                 'AdapterIndex': device.adapter_index,
                 'ChannelList':  channellist_name,
               }

    @staticmethod
    def convert_from_dict(data):
        """Restore a device from a dictionary."""

        logging.debug("Building device from dictionary.")

# TODO: We should adjust the device-path if the SN matches another device.

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

        driver = DriverDeviceFile()

        try:
            device = DriverDeviceFile.__build_device(driver,
                                                     data['Adapter'],
                                                     data['AdapterIndex'],
                                                     data['Sn'],
                                                     data['DeviceSets'],
                                                     channellist,
                                                     data['AtscType'])
        except:
            logging.exception("Could not build device for file-path [%s] "
                              "during restore." % (data['Adapter']))
            raise

        return device

    def is_available(self, device):
        """Check if the given device is still available."""

        adapter_path = device.junk_data['Adapter']
        if not exists(adapter_path):
            logging.info("Device with adapter [%s] was not found." %
                         (adapter_path))
            return False

        try:
            # Verify that it's the same device.

            try:
                sn_recalc = self.__build_sn(device.junk_data['DeviceSets'],
                                            device.address)
            except:
                logging.exception("Could not calculate SN for loaded device.")
                raise

            if device.junk_data['Sn'] != sn_recalc:
                return False
        except:
            logging.exception("Can not determine availability of device [%s]. "
                              "Indicating as unavailable." %
                              (device.identifier))
            return False

        logging.debug("Device [%s] has been verified to be available." %
                      (device.identifier))

        return True

    def iterate_channels_start(self, device, tuner_index, channel_map):
        """We expect a channels.conf file. We don't support a manual-scan."""

        raise NotImplementedError()

    def iterate_channels_next(self, state):
        """We expect a channels.conf file. We don't support a manual-scan."""

        raise NotImplementedError()

    def capture_to_file(self, tuner, writer):
        """Start streaming the feed. It is expected that the writer spawns a
        thread and returns immediately.
        """

        logging.info("Sending feed from tuner [%s] to writer [%s]." % (tuner,
                                                                       writer))

        device = tuner.device
        tuner_index = tuner.tuner_index
        adapter_filepath = device.junk_data['Adapter']

        dvr_filepath = self.__build_device_filepath(adapter_filepath,
                                                    tuner_index,
                                                    DEVICE_DVR)

        try:
            return writer.fill_from_device_file(dvr_filepath)
        except:
            logging.exception("Could not capture to file [%s]." %
                              (dvr_filepath))
            raise

    def check_tuning_status(self, tuner):
        """Return a 2-tuple of a boolean indicating if the tuning is still
        active, and the last state, if True.
        """

        # Get the tuning information for the specific device.

        state_key = None
        for key, tuning_state in self.__tuned.iteritems():
            (device_identifier, tuner_index) = key

            if device_identifier == tuner.device.identifier and \
               tuner_index == tuner.tuner_index:
                state_key = key
                break

        if state_key == None:
            message = ("Can not check state on a tuning that is not currently "
                       "active: %s" % (tuner))

            logging.error(message)
            raise Exception(message)

        queue = self.__tuned[state_key][0]

        # Convenience functions to manage the current state value.

        tuner_mgmt = cf.get(values.C_DEV_TUNER)

        def set_last_state(state):
            self.__tuned[state_key][2] = state

            logging.info("Tuning on [%s] has changed state to [%s]." %
                         (tuner, state))

            if state == TS_1_INITIAL:
                tuner_activity_type = A_TUNER_INITIAL
            elif state == TS_2_TRYING:
                tuner_activity_type = A_TUNER_TRYING
            elif state == TS_3_LOCKED:
                tuner_activity_type = A_TUNER_LOCKED
            elif state == TS_4_CANCELLED:
                tuner_activity_type = A_TUNER_CANCELLED
            else:
                raise Exception("No activity-type could be determined for "
                                "phase-type [%s]." % (state))

            try:
                tuner_mgmt.post_tuner_activity(tuner, tuner_activity_type)
            except:
                logging.exception("There was an exception while posting "
                                  "tuning-state [%s] for tuner [%s]." %
                                  (state, tuner))

        def get_last_state():
            return self.__tuned[state_key][2]

        # Look through the unprocessed messages.

        while 1:
            try:
                item = queue.get(False)
            except Queue.Empty:
                break

            last_state = get_last_state()
            (msg_type, data) = item

            # A terminal state due to an error.
            if msg_type == MT_ERROR:
                logging.error("There was an error while tuning on [%s]: %s" %
                              (tuner, data))
                continue

            # A terminal state due to a requested cancel.
            elif msg_type == MT_CANCELLED:
                set_last_state(TS_4_CANCELLED)

                logging.info("Tuning on [%s] has reported being done." %
                             (tuner))

                return (False, None)

            # Ignore anything else but status messages.
            elif msg_type != MT_STATUS:
                continue

            # If we just started and we're now seeing the status lines,
            # indicate that we're trying to lock the program.
            if last_state == TS_1_INITIAL:
                set_last_state(TS_2_TRYING)

            # If we've stated that we're trying to lock the program and we
            # -actually have- locked the program.

            elif last_state == TS_2_TRYING:

                (status, signal, snr, ber, uncorrected_blocks, \
                 is_locked) = data

                if is_locked:
                    set_last_state(TS_3_LOCKED)

        return (True, get_last_state())

    def set_vchannel(self, tuner, vchannel_scalar=None):
        """Set the vchannel on the given tuner to the given scalar. If not
        given, clear state of the tuner.
        """

        logging.info("Tuning v-channel (%s) using tuner [%s] on device [%s]." %
                     (vchannel_scalar, tuner, tuner.device))

        key = (tuner.device.identifier, tuner.tuner_index)

        # If a channel is already tuned on the given tuner, cancel it, first.
        if key in self.__tuned:
            (msg_queue, tune, last_state) = self.__tuned[key]

            try:
                tune.cancel()
            except Exception as e:
                logging.exception("Could not cancel tune on [%s]: %s" %
                                  (tuner, e))
                raise

            del self.__tuned[key]

        tuner.vchannel = vchannel_scalar

        if vchannel_scalar != None:
            queue = multiprocessing.Queue()
            tune = _TuneChannel(tuner,
                                queue
                               )

            self.__tuned[key] = [queue, tune, TS_1_INITIAL]
            tune.start()

# TODO: Make sure that the tuning process' information is cleaned-up properly.
# TODO: Make sure that the check_tuning_status() calls correctly determine the current state of the tuning process.
# TODO: Emit status standardized tuning-status messages.

            logging.info("Channel (%d) successfully tuned in separate thread." %
                         (tuner.vchannel))
        else:
            logging.info("Tuner-state cleared.")

    def __build_panels(self, panel_name_generator, notice_box, for_device):
        """Put together the panels required for additional device configuration
        after device-detection.
        """

#        tuning_info_panel_name = panel_name_generator('TuningInfo')
        atsc_type_panel_name = panel_name_generator('AtscType')

        def post_callback(sw, key, result, expression, screen):
            button = result['button']
            is_esc = result['is_esc']

            # They cancelled.
            if is_esc or is_button(button, B_CANCEL):
                raise GotoPanelException('pick_driver')

            type_mapping = {
                    B_ADAPTER_TYPE_ATSC: constants.ADAPTER_TYPE_ATSC,
                    B_ADAPTER_TYPE_DVBT: constants.ADAPTER_TYPE_DVBT,
                    B_ADAPTER_TYPE_DVBC: constants.ADAPTER_TYPE_DVBC,
                    B_ADAPTER_TYPE_DVBS: constants.ADAPTER_TYPE_DVBS,
                }

            atsc_type = None
            for this_button, this_adapter_type in type_mapping.iteritems():
                if is_button(button, this_button):
                    atsc_type = this_adapter_type

            if not atsc_type:
                raise Exception("Could not determine adapter type from button "
                                "[%s]." % (button))

        title = ('Adapter Info 2 (%s)' % (for_device.address))

        # _next will be set automatically, after generate_panels() is called.
        atsc_type_panel = { '_widget':    'choice',
                            '_name':      atsc_type_panel_name,
                            '_next':      None,
                            'title':      title,
                            'text':       'Please choice adapter type.',
                            'buttons':    [ B_ADAPTER_TYPE_ATSC,
                                            B_ADAPTER_TYPE_DVBT,
                                            B_ADAPTER_TYPE_DVBC,
                                            B_ADAPTER_TYPE_DVBS,
                                          ],
                            '_post_cb':   post_callback,
                          }

        def posthook(device, flat_results):
            """Receive the results from the driver-specific config panels. Set
            the information on the device that required user input.
            """

#            (tuning_info_results, atsc_type_results) = flat_results
            (atsc_type_results,) = flat_results

            atsc_type_button = atsc_type_results['button']

            if is_button(atsc_type_button, B_ADAPTER_TYPE_ATSC):
                atsc_type = constants.ADAPTER_TYPE_ATSC
            elif is_button(atsc_type_button, B_ADAPTER_TYPE_DVBT):
                atsc_type = constants.ADAPTER_TYPE_DVBT
            elif is_button(atsc_type_button, B_ADAPTER_TYPE_DVBC):
                atsc_type = constants.ADAPTER_TYPE_DVBC
            elif is_button(atsc_type_button, B_ADAPTER_TYPE_DVBS):
                atsc_type = constants.ADAPTER_TYPE_DVBS
            else:
                raise Exception("Could not map selected button [%s] to a ATSC "
                                "type." % (atsc_type_button))

            device.atsc_type             = atsc_type

#        panels = [tuning_info_panel, atsc_type_panel]
        panels = [atsc_type_panel]
        return (panels, atsc_type_panel, atsc_type_panel, posthook)

    def generate_panels(self, panel_name_generator, notice_box, for_device):
        """If this driver needs specific global configuration settings in order
        to tune or whatnot, return a list of additional panels. If any
        panel expressions do not have a '_next' component, it will be defaulted
        to whatever 'return_to_panel' is, above. Any data that is to be stored
        should be set on persisted_data (a dictionary).
        """

        try:
            result = self.__build_panels(panel_name_generator, notice_box,
                                         for_device)
        except:
            logging.exception("Could not build configuration panels.")
            raise

        return result

    def __get_adapters(self):
        """We expect a device path like '/dev/dvb/adapter0', and return a list
        of something like '/dev/dvb/adapter0/dvb0'.
        """

        # We only support Windows, at this time.
        if system().lower() != 'linux':
            return []

        dev_path = self.__device_search_path

        if not isdir(dev_path):
            return []

        try:
            adapter_files = [ filename \
                              for filename \
                              in listdir(dev_path) \
                              if fnmatch(filename, 'adapter*') \
                            ]
        except:
            logging.exception("Could not scan for devices in [%s]." %
                              (dev_path))
            raise

        adapter_rx = re.compile('adapter([0-9]+)$')
        adapters = []
        for filename in adapter_files:
            result = adapter_rx.match(filename)
            if result:
                adapter_filepath = ("%s/%s" % (dev_path, filename))
                adapter_index = int(result.group(1))
                adapters.append((adapter_filepath, adapter_index))

        logging.info("(%d) device(s) found in [%s]." %
                     (len(adapters), dev_path))

        return adapters

    def __get_tuners_on_adapter(self, adapter):
        """We expect a device path like '/dev/dvb/adapter0', and return a list
        of something like:
            [
             [0, 0, 0], #demux, dvr, frontend
             [1, 1, 1], #demux, dvr, frontend
            ]

        where each sublist represents the constituent devices for each tuner
        built into the device.

        We rely on the enumerate_devices() call to find real devices, and the
        deserialize routine to check if the device is still available, which
        will make sure the SN matches.
        """

        demux_rx    = re.compile('^demux([0-9]+)$')
        dvr_rx      = re.compile('^dvr([0-9]+)$')
        frontend_rx = re.compile('^frontend([0-9]+)$')

        constituents = listdir(adapter)
        device_matrix = []

        for filename in constituents:
            result = demux_rx.match(filename)
            if result:
                device_index = result.group(1)
                device_type = DEVICE_DEMUX

            if not result:
                result = dvr_rx.match(filename)
                if result:
                    device_index = result.group(1)
                    device_type = DEVICE_DVR

            if not result:
                result = frontend_rx.match(filename)
                if result:
                    device_index = result.group(1)
                    device_type = DEVICE_FRONTEND

            if not result:
                continue

            device_index = int(device_index)

            if device_index >= len(device_matrix):
                device_matrix.append([None, None, None])

            device_matrix[device_index][device_type] = True

        # Grab each tuner (where each has a device file of every type) and add
        # to a second list.

        device_sets = []
        index = 0
        for unvalidated_device_set in device_matrix:
            okay = True
            for device in unvalidated_device_set:
                if not device:
                    okay = False
                    break

            if okay:
                # There's no way we can get here without having all three
                # devices having the same index. Just add the same index three
                # times to build the device_set.
                device_sets.append([index, index, index])

            index += 1

        logging.info("(%d) tuner(s) found on adapter [%s]." %
                     (len(device_sets), adapter))

        return device_sets

    @property
    def name(self):
        """Returns a nice, human-readable name for this driver."""

        return 'RawDevice'

    @property
    def description(self):
        """Returns a string that describes the type of device that we handle.
        """

        return "Read from a /dev/dvb/adapter<n> device using a channels.conf" \
               " file."

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

        return False

