import sys
import logging

from os import remove
from twisted.python.log import startLogging
#from twisted.internet.defer import Deferred
from twisted.internet import reactor, protocol

from tv_server.config.backend import pipe_filepath
from tv_server.read_buffer import ReadBuffer
from tv_server.backend import serialize_message
from tv_server.backend.protocol.error_pb2 import error


class WaitForQueries(protocol.Protocol):
    def __init__(self):
        self.__buffer = ReadBuffer()
    
    def dataReceived(self, data):
        try:
            self.__buffer.push(data)

            message_tuple = self.__buffer.read_message()
            if message_tuple is None:
                return

            (message, from_thread_id, to_thread_id) = message_tuple

            # Send the message to a handling method named similarly. If it
            # returns something other than NULL, we assume that its a message
            # to be serialized and written back. Only the client observes the
            # "to_thread_id" value.

            message_type_name = message.__class__.__name__
            name_parts = message_type_name.split('_')
            
            if len(name_parts) != 2:
                logging.error("Can't process message with unclassifiable type "
                              "[%s]." % (message_type_name))
                return

            (handler_type_name, action_name) = name_parts
            handler_module_path = 'tv_server.backend.handlers.' + \
                                  handler_type_name + \
                                  "_handler"

            handler_class_name = handler_type_name.capitalize() + "Handler"
            
            try:
                handler_module = __import__(handler_module_path, \
                                            fromlist=[handler_class_name])
            except:
                logging.exception("Can't process message with invalid "
                                  "handling module [%s] and class [%s]." % 
                                  (handler_module_path, handler_class_name))
                return

            handler_cls = getattr(handler_module, handler_class_name)            
            handle_method = ('handle%s' % (action_name.capitalize()))
    
            response = getattr(handler_cls(), handle_method)(message)
            if response is None:
                return

            raw_message = serialize_message(response, from_thread_id)
            self.transport.write(raw_message)

#        self.transport.loseConnection()

        except Exception as e:
            logging.exception("There was an error while acting on incoming "
                              "data.")

            exc_type = sys.exc_info()[0]

            response = error()
            response.version = 1
            response.type = exc_type.__class__.__name__
            response.message = str(e)
            
            self.transport.write(response.SerializeToString())

    def connectionMade(self):
        print("Connection made.")

    def connectionLost(self, reason):
        print("Connection lost.")


def start_server():
    startLogging(sys.stdout)

    serverFactory = protocol.ServerFactory()
    serverFactory.protocol = WaitForQueries

    try:
        remove(pipe_filepath)
    except:
        pass
    
    reactor.listenUNIX(pipe_filepath, serverFactory)
    reactor.run()
