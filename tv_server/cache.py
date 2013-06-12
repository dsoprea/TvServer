import memcache


class Cache(object):
    def __init__(self):
        self.__client = memcache.Client(['127.0.0.1:11211'], debug=0)

    def set(self, k, v, time=0):
        return self.__client.set(k, v, time)

    def get(self, k):
        return self.__client.get(k)
