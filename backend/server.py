import sys
import logging

from twisted.python.log import startLogging
#from twisted.internet.defer import Deferred
from twisted.internet import reactor, protocol

from config.backend import pipe_filepath
from read_buffer import ReadBuffer
from backend.handlers import Handlers
from backend.common import serialize_message

class WaitForQueries(protocol.Protocol):
    def __init__(self):
        self.__buffer = ReadBuffer()
        self.__handlers = Handlers()
    
    def dataReceived(self, data):
        try:
            self.__buffer.push(data)

            message = self.__buffer.read_message()
            if message is None:
                return

            # Send the message to a handling method named similarly. If it
            # returns something other than NULL, we assume that its a message
            # to be serialized and written back.

            message_type_name = message.__class__.__name__
            handle_method = ('handle%s' % (message_type_name.capitalize()))
    
            response = getattr(self.__handlers, handle_method)(message)
            if response is None:
                return

            raw_message = serialize_message(response)
            self.transport.write(raw_message)

#        self.transport.loseConnection()

        except:
            logging.exception("There was an error while acting on incoming "
                              "data.")
            raise

    def connectionMade(self):
        print("Connection made.")

    def connectionLost(self, reason):
        print("Connection lost.")


def start_server():
    startLogging(sys.stdout)

    serverFactory = protocol.ServerFactory()
    serverFactory.protocol = WaitForQueries

    reactor.listenUNIX(pipe_filepath, serverFactory)
    reactor.run()