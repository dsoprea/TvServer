from copy import deepcopy

from tv_server.big_id import BigId

from tv_server.device.drivers import driverdvbchar
from tv_server.device.drivers import driverhdhomerun

available_drivers = \
    { driverdvbchar.DriverDvbChar.__name__: \
        (driverdvbchar.DriverDvbChar, driverdvbchar.DeviceDvbChar),
      driverhdhomerun.DriverHdHomeRun.__name__: \
        (driverhdhomerun.DriverHdHomeRun, driverhdhomerun.DeviceHdHomeRun) }

def get_big_id_from_device(device):
 
    return BigId().push(device.driver.__class__.__name__).\
                   push(device.identifier)

def get_device_from_big_id(big_id_):
    big_id = deepcopy(big_id_)
    
    device_id = big_id.pop()
    dcn = big_id.pop()
    
    return available_drivers[dcn][0]().build_from_id(device_id)
    