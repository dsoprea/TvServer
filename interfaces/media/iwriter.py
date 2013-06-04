class IWriter(object):
    """A class that implements methods that will provide all media copy/writing 
    handling. All such internal actions should be offloaded to another thread, 
    and return immediately.
    """

    def fill_from_device_file(self, file_path):
        """Start a continuous copy operation between the given character-device 
        and the given output file.
        """
    
        raise NotImplementedError()

    def is_active(self):
        """Is a write task currently going on?"""
    
        raise NotImplementedError()

    def stop(self):
        """Stop the write task."""
    
        raise NotImplementedError()

    def error_state(self):
        """If there was a terminal exception during the write, return it."""
    
        raise NotImplementedError()

