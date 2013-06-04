"""A collection of library-type functionality/functionalities for keeping track 
of what has been exchanged with clients.
"""

class IClientCollection(object):
    def get(hostname, create_if_missing=True):
        """Get an instance of ClientState for the given hostname."""
        
        raise NotImplementedError()

