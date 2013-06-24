from tv_server.big_id import BigId


class ChannelsConfRecord(object):
    def __init__(self, name, freq, mod, vid, aid, sid):
        self.__name = name
        self.__frequency = freq
        self.__modulation = mod
        self.__video_id = int(vid)
        self.__audio_id = int(aid)
        self.__stream_id = int(sid)

        self.__identifier = repr(BigId().push(name).\
                                         push(freq).\
                                         push(mod).\
                                         push(vid).\
                                         push(aid).\
                                         push(sid))

    @staticmethod
    def build_from_id(id_):
        big_id = BigId(id_)
        
        stream_id = big_id.pop()
        audio_id = big_id.pop()
        video_id = big_id.pop()
        modulation = big_id.pop()
        frequency = big_id.pop()
        name = big_id.pop()

        return ChannelsConfRecord(name, frequency, modulation, video_id, 
                                  audio_id, stream_id)

    def __str__(self):
        return ('<CC VID=[%s] AID=[%s] SID=[%s]>' % 
                (self.__video_id, self.__audio_id, self.__stream_id))

    def __repr__(self):
        return ('<CC NAME=[%s] F=[%s] M=[%s] V=[%d] A=[%d] S=[%d]>' % 
                (self.__name, self.__frequency, self.__modulation, 
                 self.__video_id, self.__audio_id, self.__stream_id))

    @property
    def identifier(self):
        return self.__identifier

    @property        
    def name(self):
        return self.__name

    @property
    def frequency(self):
        return self.__frequency
    
    @property
    def modulation(self):
        return self.__modulation
    
    @property
    def video_id(self):
        return self.__video_id
    
    @property
    def audio_id(self):
        return self.__audio_id
    
    @property
    def stream_id(self):
        return self.__stream_id

