import re

from rain.common.utility import aggregate_from_data_file_with_key

from logging import getLogger
logging = getLogger(__name__)

def parse_channels_conf(file_path):

    def validate(row):
        for key in ['Frequency', 'VideoId', 'AudioId', 'ProgramId']:
            value = row[key]
            if not re.match('^[0-9]+$', value):
                return False

        row['ProgramId'] = int(row['ProgramId'])
        row['VideoId'] = int(row['VideoId'])
        row['AudioId'] = int(row['AudioId'])

        return True

    columns = ['Name', 'Frequency', 'Modulation', 'VideoId', 'AudioId', 'ProgramId']
    key_column = 'ProgramId'

    try:
        return aggregate_from_data_file_with_key(file_path, columns, 
                                                 key_column, validate, 
                                                 separator=':')
    except:
        logging.exception("Channels data parse error.")
        raise

