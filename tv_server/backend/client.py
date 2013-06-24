import socket
import logging

from threading import Lock, current_thread

from tv_server.config.backend import pipe_filepath, backend_block_size_bytes, \
                                     client_read_timeout_s

from tv_server.read_buffer import ReadBuffer
from tv_server.backend import ResponseTimeout, serialize_message

class Client(object):
    __locker_buffer = Lock()
    __locker_mailbox = Lock()
    
    __buffer = ReadBuffer()
    __mailboxes = {}
    
    def __wait_for_one(self, s):
        cls = self.__class__
        
        # The socket-read and the buffer-affecting routines need to have the
        # same lock. We can't have data be inserted into the buffer out-of-
        # order, so the socket-read and the buffer-insert must happen 
        # atomically. Simultaneously, we have to have all buffer operations
        # happen in a thread-safe manner, so the read and the write must have
        # the same lock. Therefore, we must use the same lock for all three.
        # We can, however, stop locking between the buffer-write and buffer-
        # read, briefly.        
        
        # Read data from the server, and push into the buffer. Once no more
        # data is readily available, sift [any] buffered messages.
        while 1:
            with cls.__locker_buffer:
                try:
                    data = s.recv(backend_block_size_bytes)
                except socket.timeout:
                    raise ResponseTimeout("The server did not respond in time.")
                else:
                    if data:
                        cls.__buffer.push(data)
                    
                    if len(data) < backend_block_size_bytes:
                        break

        # Parse through any messages that were received. Push any messages not
        # directed to our thread into a mailbox for the corresponding thread.    
        while 1:
            with cls.__locker_buffer:
                message_tuple = cls.__buffer.read_message()
                if message_tuple is None:
                    raise Exception("No message was [completely] returned by server.")

                # The message is always from the server, so we ignore that ID.       
                (message, from_thread_id, to_thread_id) = message_tuple
                logging.debug("Mailboxing message [%s] intended for thread "
                              "with ID (%X)." % 
                              (message.__class__.__name__, to_thread_id))

            with cls.__locker_mailbox:
                # Store the incoming message, which wasn't necessarily intended for 
                # our thread.
                # 
                # Gracefully handle messages received for threads that may no
                # longer exist.
                try:                
                    cls.__mailboxes[to_thread_id].append(message)
                except:
                    pass 
    
            with cls.__locker_mailbox:
                # Check whether we've received a message either from this thread or 
                # any other and return.
                thread_id = cls.__get_thread_id()
                
                try:
                    message = cls.__mailboxes[thread_id][0]
                except:
                    pass
                else:
                    logging.debug("We've received targeted message [%s] [%X]." % 
                                  (message.__class__.__name__, thread_id))
    
                    return message
        
    def __raw_send(self, data):
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.settimeout(client_read_timeout_s)
        s.connect(pipe_filepath)

        i = 0
        while i < (len(data) - 1):
            num_sent = s.send(data[i:])
            i += num_sent
        
        response = self.__wait_for_one(s)
        s.close()

        return response

    @classmethod
    def __get_thread_id(cls):
        return current_thread().ident

    @classmethod
    def create_mailbox(cls):
        thread_id = cls.__get_thread_id()
        
        with cls.__locker_mailbox:
            logging.debug("Creating mailbox for thread with ID [%X]." % 
                          (thread_id))
            
            cls.__mailboxes[thread_id] = []

    @classmethod
    def destroy_mailbox(cls):
        thread_id = cls.__get_thread_id()
        
        with cls.__locker_mailbox:
            logging.debug("Destroying mailbox for thread with ID [%X)." % 
                          (thread_id))
            
            del cls.__mailboxes[thread_id]

    def send_query(self, message):
        logging.debug("Sending [%s] message." % (message.__class__.__name__))
        
        raw_message = serialize_message(message)
        
        logging.debug("Message of type [%s] serialized to (%d) bytes." % 
                      (message.__class__.__name__, len(raw_message)))

        response = self.__raw_send(raw_message)
        
        return response

