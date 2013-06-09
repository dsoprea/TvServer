import socket

from config.backend import pipe_filepath, backend_block_size_bytes, \
                           client_read_timeout_s

from read_buffer import ReadBuffer
from backend import ResponseTimeout
from backend import serialize_message

class Client(object):
    def __init__(self):
        self.__buffer = ReadBuffer()
    
    def __wait_for_one(self, s):
        while 1:
            try:
                data = s.recv(backend_block_size_bytes)
            except socket.timeout:
                raise ResponseTimeout("The server did not respond in time.")
            else:
                if data:
                    self.__buffer.push(data)
                
                if len(data) < backend_block_size_bytes:
                    break
    
        message = self.__buffer.read_message()
        if message is None:
            raise Exception("No message was [completely] returned by server.")
    
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

    def send_query(self, message):
        raw_message = serialize_message(message)
        response = self.__raw_send(raw_message)
        
        return response
