import logging

from collections import OrderedDict
from random import random
from math import floor
from web.webapi import NotFound, BadRequest, OK
from web import debug, header

_PAGE_SIZE = 4

# Technically, we don't need OrderedDict since we use _keys for pagination. 
# We're using it because we've been asked to -store- them in the order 
# received, though.
_values = OrderedDict()
_keys = []

def _get_pair_string(k, v):
    return ("%s -> %s" % (k, v))

class _HandlerBase(object):
    def __init__(self, *args, **kwargs):
         header('Content-Type', 'text/plain')

    def GET(self, *args, **kwargs):
        """Return a 400, unless implemented (per spec)."""
    
        return BadRequest()

    def POST(self, *args, **kwargs):
        """Return a 400, unless implemented (per spec)."""

        return BadRequest()

class Fail(_HandlerBase):
    """Receives all requests to bad URLs."""

    pass

class EntryPost(_HandlerBase):
    """Store into the dictionary."""

    def POST(self, key, value):
        global _values
        global _keys
        
        if len(key) >= 128 or len(value) >= 128:
            return BadRequest()

        # Store the value. Only append to _keys if we're adding it for the 
        # first time.
        
        try:
            _values[key]
        except:
            _keys.append(key)
        finally:
            _values[key] = value

        return OK()


class EntryGet(_HandlerBase):
    """Return the value for a specific key."""

    def GET(self, key):
        try:
            return _values[key]
        except:
            return NotFound()


class EntryRandom(_HandlerBase):
    """Return a random pair."""

    def GET(self):
        if not _values:
            return NotFound()
        
        i = int(floor(random() * len(_keys)))
        key = _keys[i]
        value = _values[key]

        return _get_pair_string(key, value)


class EntryList(_HandlerBase):
    """Return the stored pairs."""

    def GET(self, page):
        page = int(page)

        count = len(_keys)
        i = page * _PAGE_SIZE

        buf = ''
        for j in xrange(i, i + _PAGE_SIZE):
            if j >= count:
                break

            key = _keys[j]
            buf += _get_pair_string(key, _values[key]) + "\n"

        return buf

