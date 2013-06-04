import json

from web.webapi import BadRequest
from web import header

def split_parameters(raw_string):
    if not raw_string:
        return {}
    
    parts = raw_string.split('/')
    if len(parts) % 2 == 1:
        parts.add('')
    
    return dict([(parts[i], parts[i + 1]) \
                for i \
                in xrange(len(parts)) \
                if i % 2 == 0])


class HandlerBase(object):
    def __init__(self, *args, **kwargs):
        pass

    def GET(self, *args, **kwargs):
        """Return a 400, unless implemented (per spec)."""
    
        return BadRequest()

    def POST(self, *args, **kwargs):
        """Return a 400, unless implemented (per spec)."""

        return BadRequest()

    def json_response(self, data):
        print(data)
        
        header('Content-Type', 'application/json')
        return json.dumps(data)


class GetHandler(HandlerBase):
    def GET(self, method, ignore_me=None, parameters_raw=None):
        parameters = split_parameters(parameters_raw)

        return getattr(self, method)(**parameters)


class Fail(HandlerBase):
    """Receives all requests to bad URLs."""

    pass

