CHANNELTYPE_NUMBER = 'number'
CHANNELTYPE_NAME   = 'name'

UPCOMINGFLAGS_BYSERIES  = 1
UPCOMINGFLAGS_BYCHANNEL = 2
UPCOMINGFLAGS_BYTIME    = 4
UPCOMINGFLAGS_WITHDUPS  = 8

class ISchedule(object):
    def update(self, from_date, to_date):
        """Retrieve updates for the given date range, and apply them."""

        raise NotImplementedError()
    
    def optimize(self):
        """Build indices/etc after all of the data has been updated. This
        has been split into another method so that the system can log which 
        phase it's in, tell the user what phase we're in, etc..
        """
        
        raise NotImplementedError()

    def cleanup(self):
        """Do regular maintenance."""
    
        raise NotImplementedError()

    def get_data_for_guide(self, lineup_id, from_timestamp, to_timestamp):
        """Return an aggregate of all data that should be presented in the 
        guide screen from the given lineup-ID in the given timeframe.
        """

        raise NotImplementedError()

    def search_programs(self, lineup_id, phrase):
        """Search the titles, descriptions, actors, etc.. for the given phrase."""
    
        raise NotImplementedError()

    def get_program_by_time_and_channel(self, lineup_id, timestamp, channel,
                                        channel_type=CHANNELTYPE_NUMBER):
        """Derive a program-ID using the lineup, time, and channel."""

        raise NotImplementedError()

    def get_program(self, lineup_id, program_id):
        """Get program information by ID."""
    
        raise NotImplementedError()

    def get_upcoming(self, lineup_id, flags, series_id=None, channel=None, 
                     timestamp=None, channel_type=CHANNELTYPE_NUMBER):
        """Get upcoming programs in the lineup based on the given criteria. 
        This is a required component of the scheduler.
        """

        raise NotImplementedError()

    def initialize(self):
        """Create initial configurations and structures to store the 
        information.
        """

        raise NotImplementedError()

