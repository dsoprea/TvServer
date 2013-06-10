import sha
import re

from multiprocessing import Process, Queue, Event
from os.path import isfile, isdir, exists, basename
from os import listdir, stat, minor, major, kill
from fnmatch import fnmatch
from platform import system
from signal import SIGALRM

from pyzap.calls import c_azap_tune_silent
from pyzap.types import TUNER_DESCRIPTOR, ATSC_TUNE_INFO, STATUS_RECEIVER_CB
from pyzap.constants import modulation

import log_config

#from rain_config import constants, values, channel_config, \
#                                routine_close_priority

from interfaces.device.itunerdriver import ITunerDriver, TD_TYPE_CHANNELSCONF
from interfaces.device.itunerdevice import ITunerDevice
from interfaces.device.ituner import *
from device.tuner_device_common import TunerDeviceCommon
from device import DeviceDoesNotExist

from managed_routine import ManagedRoutine

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


class DeviceDvbChar(TunerDeviceCommon, ITunerDevice):
    """Represents a device enumerated via DriverDvbChar."""

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
        """Return an adapter-filepath."""

        return self.address

    @property
    def address(self):
        """Returns the DVB file-path."""

        return self.__adapter

    @property
    def junk_data(self):
        """Returns an object of an unspecified type that the driver knows how
        to interpret. Used for implementation-specific data to be passed from
        the device to the driver.
        """

        return { 'DeviceSets': self.__device_sets,
                 'AtscType': self.__atsc_type,
                 'Adapter': self.__adapter,
                 'Sn': self.__sn,
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

    def __hash__(self):
        return hash(self.identifier)

    def __eq__(self, o):
        return (hash(self) == hash(o)) 

    def __ne__(self, o):
        return (hash(self) != hash(o))

    
class _ExecuteError(Exception):
    """There was a failure executing an external command."""

    def __init__(self, retval):
        Exception.__init__(self, "Command failed with (%d)." % (retval))


# TODO: Update the channels-conf references for our channel-list concept.

class _TuneChannel(Process, ManagedRoutine):
    """The multiprocessing process that invokes the external utilities to tune
    channels.
    """

    __tuner                 = None
    __msg_queue             = None
    __cancel_event          = None

    def __init__(self, tuner, msg_queue):
        name = ('TuneChannel-%s' % (str(tuner)))
        super(_TuneChannel, self).__init__(name=name)

# TODO: Reimplement priorities later.
# routine_close_priority.P_TUNING_THREAD
        priority = 10
        ManagedRoutine.__init__(self, name, priority)

        self.__tuner        = tuner
        self.__msg_queue    = msg_queue
        self.__cancel_event = Event()

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

        logging.debug("Executing tune.")

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

        name           = tuner.tune_data.name
        frequency      = tuner.tune_data.frequency
        modulation_raw = tuner.tune_data.modulation
        video_id       = tuner.tune_data.video_id
        audio_id       = tuner.tune_data.audio_id
        program_id     = tuner.tune_data.program_id

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

        is_cancelled = lambda: self.is_cancelled()

        def status_receiver(status, signal, snr, ber, uncorrected_blocks, \
                            is_locked):
            if is_cancelled():
                logging.debug("Tune has been cancelled. Instructing tuning "
                              "library to quit.")

                return 0
            
            try:
                status_package = (status, signal, snr, ber,
                                  uncorrected_blocks, is_locked)

                logging.debug("Received status:\n%s" % (status_package,))

                self.__msg_queue.put((MT_STATUS, status_package))

                return 1
            except KeyboardInterrupt:
                # We don't recognize a keyboard break in this context.
                return 1

#            print('%X' % status)
#            print('%X' % signal)
#            print('%X' % snr)
#            print('%X' % ber)
#            print('%X' % uncorrected_blocks)
#            print('%X' % is_locked)

        logging.debug("Invoking tune call.")

        try:
            c_azap_tune_silent(descriptor, atsc_tune_info, 1,
                               STATUS_RECEIVER_CB(status_receiver))
        except:
            logging.exception("There was an exception while doing the "
                              "low-level tuning.")
            raise

    def cancel(self):
        """Stop tuning the channel. Called by original process. This call must
        block until the thread has finished.
        """

        logging.info("Cancelling tune on [%s]." % (self.__tuner))

        self.__cancel_event.set()

        logging.info("Sending SIGALRM to PID (%d) to cancel tuning." % 
                     (self.pid))

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
        return self.__cancel_event.is_set()


class DriverDvbChar(ITunerDriver):
    """Represents an interface to a device represented by a
    /dev/dvb/adapter<n> device.
    """

    __atsc_type             = None

    __tuned                 = {}

    __device_search_path = '/dev/dvb'

    def build_from_id(self, id_):
        """Our id is the filepath of the adapter."""
        
        adapter_filepath = id_
        adapter_filename = basename(adapter_filepath)
        
        adapter_rx = re.compile('adapter([0-9]+)$')
        result = adapter_rx.match(adapter_filename)
        if not result:
            raise Exception("ID [%s] for driver-device is not the correct format.")
            
        adapter_index = int(result.group(1))
        
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
            device = DriverDvbChar.__build_device(self,
                                                     adapter_filepath,
                                                     adapter_index,
                                                     sn,
                                                     device_sets)
        except:
            logging.exception("Could not build device for adapter [%s] "
                              "during enumeration." % (adapter_filepath))
            raise

        return device

    def enumerate_devices(self):
        """List available devices."""

        try:
            adapters = self.__get_adapters()
        except Exception as e:
            logging.exception("Devices error: %s" % (str(e)))
            raise

        devices = []
        for adapter_filepath in adapters:
            device = self.build_from_id(adapter_filepath)

# If the SN has been given, check it against what we can calculate, here, and
# tell the system to ignore the device if the SNs don't match (the device is
# not present).

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
            return DeviceDvbChar(driver,
                                 adapter,
                                 adapter_index,
                                 device_sets,
                                 sn,
                                 channellist,
                                 atsc_type)
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
                logging.exception("Could not restore DriverDvbChar device with "
                                  "broken channel-list: %s" % (data))
                raise

        driver = DriverDvbChar()

        try:
            device = DriverDvbChar.__build_device(driver,
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

    def tune(self, tuner, cc_record=None):
        """Set the vchannel on the given tuner to the given channel data. If 
        not given, clear state of the tuner.
        """

        logging.info("Tuning using tuner [%s] on device [%s]:\n%s" %
                     (tuner, tuner.device, cc_record))

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

            tuner.tune_data = None
            del self.__tuned[key]

        tuner.tune_data = cc_record

        if cc_record is not None:
            queue = Queue()
            tune = _TuneChannel(tuner, queue)

            self.__tuned[key] = [queue, tune, TS_1_INITIAL]
            tune.start()

# TODO: Make sure that the tuning process' information is cleaned-up properly.
# TODO: Make sure that the check_tuning_status() calls correctly determine the current state of the tuning process.
# TODO: Emit status standardized tuning-status messages.

            logging.info("Tune operation started in separate process:\n%s" %
                         (tuner.tune_data))
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
                adapters.append(adapter_filepath)

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

        try:
            constituents = listdir(adapter)
        except OSError:
            raise DeviceDoesNotExist("Adapter path [%s] may no longer exist." % 
                                     (adapter))
            
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

        return 'DvbCharDevice'

    @property
    def description(self):
        """Returns a string that describes the type of device that we handle.
        """

        return "Read from a /dev/dvb/adapter<n> device using channels.conf " \
               "data passed via parameters."

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

    @property
    def tuner_data_type(self):
        """Returns one of the TD_TYPE_* values (above)."""

        return TD_TYPE_CHANNELSCONF 

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, o):
        return (hash(self) == hash(o)) 

    def __ne__(self, o):
        return (hash(self) != hash(o))
