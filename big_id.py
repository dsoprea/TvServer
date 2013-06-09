"""A collection of functionality for successively wrapping one ID with many 
others. This is necessary if we want to create an ID that's complete enough
to retrieve a resource, but which depends on other IDs. Specificity-based 
cascading (principal ID wraps the IDs on which it depends).
"""

import re

from base64 import urlsafe_b64encode, urlsafe_b64decode

class BigId(object):
    def __init__(self, flat_big_id=None):
        self.__stack = []

        if flat_big_id is not None:
            flat_big_id = str(flat_big_id)
            while flat_big_id != '':
                matched = re.match('^[^=]+=+', flat_big_id)
                
                # We'll always end with an extra '='. Clip it.
                encoded_id = matched.group(0)[:-1]

                flat_big_id = flat_big_id[len(encoded_id) + 1:]

                self.push(encoded_id, True)
    
    def push(self, id_, raw=False):
        
        id_ = str(id_)
        encoded = urlsafe_b64encode(id_) if raw is False else id_
        
        # Make sure that we always end with at least one '='. This is the only 
        # symbol that we can safely handle.
        self.__stack.append(encoded + '=')
        
        return self
        
    def peek_last(self):
        if not self.__stack:
            raise Exception("Big ID is empty.")
        
        return urlsafe_b64decode(self.__stack[-1])

    def pop(self):
        if not self.__stack:
            raise Exception("Big ID is empty.")

        encoded = self.__stack.pop()
        return urlsafe_b64decode(encoded)

    def __repr__(self):
        return ''.join(self.__stack)
