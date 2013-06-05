import logging

from collections import OrderedDict
from random import random
from math import floor
from web.webapi import NotFound, BadRequest, OK
from web import debug, header
from handlers import GetHandler

from datetime import datetime

from rain_config import values, routine_close_priority

from rain.common.modules import cf
from rain.common.modules.pipe_writer import PipeWriter
from rain.dvr.interfaces.ieventhandler import IEventHandler
from rain.dvr.modules.device.tuner_info import TunerInfo

from logging import getLogger
logging = getLogger(__name__)


class ExperienceHandler(GetHandler):
    def allocate_handler(self, event_message, response_event_name):
        logging.info("Host [%s] wants to allocate a tuner." %
                     (event_message.hostname))

# TODO: Also, allow a specific device to be requested.
        try:
            allocation_data = event_message.payload['allocation_data']
        except:
            logging.exception("Event data is not correct for start_frontend.")
            raise

        tuner_mgmt = cf.get(values.C_DEV_TUNER)

        try:
            tuner = tuner_mgmt.request_tuner(allocation_data)
        except:
            logging.exception("Error while acquiring tuner.")
            raise

        if tuner:
            logging.info("Tuner [%s] has been allocated for host [%s]." %
                         (tuner, event_message.hostname))

            tuner_serialized = TunerInfo.serialize(tuner)

            # Remember what tuner has been allocated for this client.
            self.__get_client_state(event_message).add_tuner(tuner_serialized)
        else:
            logging.info("No tuner was available for allocation by host "
                         "[%s]." % (event_message.hostname))

            tuner_serialized = None

        data = { 'Tuner': tuner_serialized }

        event_message.respond(event_message.event_type,
                              response_event_name,
                              data)

# TODO: !! Emit an ERROR message when there's a problem with handling a request.
    def handle_tune_channel(self, event_message, response_event_name):

        logging.info("Host [%s] wants to tune a tuner." %
                     (event_message.hostname))

        try:
            tuner_serialized = event_message.payload['Tuner']
            channel_number = int(event_message.payload['ChannelNumber']) \
                                if 'ChannelNumber' \
                                in event_message.payload \
                                else None

            channel_name = event_message.payload['ChannelName'] \
                                if 'ChannelName' \
                                in event_message.payload \
                                else None
        except:
            logging.exception("Event data is not correct for tuner_channel.")
            raise
# TODO: Implement.
        if channel_name:
            raise NotImplementedError("Channel-names are not supported, yet.")

        # Verify authorization for tuner.

        if not self.__get_client_state(event_message).has_tuner(tuner_serialized):
            logging.error("Hostname [%s] is not authorized for tuner [%s]." %
                          (event_message.hostname, tuner_serialized))
            raise

        try:
            tuner = TunerInfo.unserialize(tuner_serialized)
        except:
            logging.exception("Could not restore tuner: %s" % (tuner_serialized))
            raise

        logging.info("Host [%s] wants to tune tuner [%s]." %
                     (event_message.hostname, tuner))

        # Set channel.

        try:
            tuner.easy_set_vchannel(channel_number)
        except:
            logging.exception("Could not set tuner [%s] to channel [%d]." %
                              (tuner, channel_number))
            raise

        # Tuning status will be sent via regular tuning-related events to
        # client.

        data = { 'Response':      'ok',
                 'Tuner':         tuner_serialized,
                 'ChannelNumber': channel_number,
                 'ChannelName':   channel_name }

        event_message.respond(event_message.event_type,
                              'tune_channel_response',
                              data)

    def handle_stop_recording(self, event_message, response_event_name):
# TEMP: This is just a PoC for getting the video into a file.

        try:
            tuner_serialized = event_message.payload['Tuner']
        except:
            logging.exception("Event data is not correct for stop_recording.")
            raise

        # Verify authorization for tuner.

        if not self.__get_client_state(event_message).has_tuner(tuner_serialized):
            logging.error("Hostname [%s] is not authorized for tuner [%s]." %
                          (event_message.hostname, tuner_serialized))
            raise

        try:
            tuner = TunerInfo.unserialize(tuner_serialized)
        except:
            logging.exception("Could not restore tuner: %s" % (tuner_serialized))
            raise

        client_collection = cf.get(values.C_CLIENT_CLIENTCOLLECTION)
        hostname = event_message.hostname

        logging.info("Host [%s] wants to stop recording on tuner [%s]." %
                     (event_message.hostname, tuner))

        client_state = client_collection.get(hostname)

        try:
            client_state.clear_writer(tuner_serialized)
        except:
            logging.exception("Could not clear writer for tuner [%s]." %
                              (tuner_serialized))
            raise

        logging.info("Writer for hostname [%s] and tuner [%s] stopped." %
                     (hostname, tuner))

    def handle_start_recording(self, event_message, response_event_name):
# TEMP: This is just a PoC for getting the video into a file.

        try:
            tuner_serialized = event_message.payload['Tuner']
        except:
            logging.exception("Event data is not correct for start_recording.")
            raise

        # Verify authorization for tuner.

        if not self.__get_client_state(event_message).has_tuner(tuner_serialized):
            logging.error("Hostname [%s] is not authorized for tuner [%s]." %
                          (event_message.hostname, tuner_serialized))
            raise

        try:
            tuner = TunerInfo.unserialize(tuner_serialized)
        except:
            logging.exception("Could not restore tuner: %s" % (tuner_serialized))
            raise

        logging.info("Host [%s] wants to record on tuner [%s]." %
                     (event_message.hostname, tuner))

        # Build writer.

        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        output_filepath = ("/tmp/%s" % (timestamp))

#        transferred = 0

        def progress_callback(write_method, status_data):
            if write_method != 'character_copy':
                raise Exception("Progress-callback expected method "
                                "'character_copy'.")

            (transferred, block_size) = status_data

            print("Transferred: %d" % (transferred))

        try:
            writer = PipeWriter(output_filepath, None, progress_callback,
                                routine_close_priority.P_PIPEWRITER_THREAD)
        except:
            logging.exception("Could not build writer.")
            raise

        client_collection = cf.get(values.C_CLIENT_CLIENTCOLLECTION)
        hostname = event_message.hostname

        client_state = client_collection.get(hostname)
        client_state.set_writer(tuner_serialized, writer)

        try:
            tuner.device.driver.capture_to_file(tuner, writer)
        except:
            logging.exception("Could not start capture of tuner [%s] with "
                              "writer [%s]." % (tuner, writer))
            raise
