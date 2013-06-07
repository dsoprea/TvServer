import json

from web.webapi import BadRequest
from web import header


class RequestError(Exception):
    pass

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

    def json_response(self, data=None):
        header('Content-Type', 'application/json')
        return json.dumps({ 'Error': None, 'Data': data })

    def json_error(self, message, error_type_name, data=None):
        header('Content-Type', 'application/json')
        return json.dumps({ 'Error': error_type_name,
                            'Message': message, 
                            'Data': data })


class GetHandler(HandlerBase):
    def __init__(self, returns_json=True):
        self.__returns_json = returns_json
    
    def GET(self, method, ignore_me=None, parameters_raw=None):
        parameters = split_parameters(parameters_raw)

        try:
            response = getattr(self, method)(**parameters)
        except Exception as e:
            message = str(e)
            return self.json_error(message, e.__class__.__name__) \
                    if self.__returns_json \
                    else message
        else:
            return self.json_response(response)


class Fail(HandlerBase):
    """Receives all requests to bad URLs."""

    pass

    
