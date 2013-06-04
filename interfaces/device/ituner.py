# Activity types.
A_ALLOCATED       = '1_allocated'
A_TUNER_INITIAL   = '2_initial'
A_TUNER_TRYING    = '3_trying'
A_TUNER_LOCKED    = '4_locked'
A_TUNER_CANCELLED = '5_cancelled'
A_STATUS          = '6_status'
A_RELEASED        = '7_released'

TUNER_ACTIVITY_TYPES = [ A_TUNER_INITIAL,
                         A_TUNER_TRYING,
                         A_TUNER_LOCKED,
                         A_TUNER_CANCELLED ]

class ITuner(object):

    def get_default_tuner_index(self, device):
        """When a tuner is required, start with the index that we return."""
        
        raise NotImplementedError()
        
    def get_next_tuner_index(self, device, current_index):
        """When another tuner is required, return the next one to be 
        used/attempted.
        """

        raise NotImplementedError()

    def update_tuners(self):
        """Notify The tuner class that there has been a tuner-related
        configuration change.
        """
    
        raise NotImplementedError()
    
    def register_listener(self, update_cb, specific_tuner=None):
        """Register a tuner-change event listener."""
    
        raise NotImplementedError()
    
    def remove_listener(self, update_cb, specific_tuner=None):
        """Deregister a tuner-change event listener."""
    
        raise NotImplementedError()
    
    def request_tuner(self, allocation_data=None):
        """Reserve a tuner."""
    
        raise NotImplementedError()
    
    def post_tuner_activity(self, specific_tuner, activity_type):
        """This is meant to receive phase updates during the tuning process."""

        raise NotImplementedError()

    def release_tuner(self, device, tuner_index):
        """Indicate that a tuner has become available again."""
    
        raise NotImplementedError()
    
    def get_statuses(self):
        """Get status of all tuners on all devices."""
    
        raise NotImplementedError()

