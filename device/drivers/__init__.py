from device.drivers import driverdvbchar
from device.drivers import driverhdhomerun

available_drivers = \
    { driverdvbchar.DriverDvbChar.__name__: \
        (driverdvbchar.DriverDvbChar, driverdvbchar.DeviceDvbChar),
      driverhdhomerun.DriverHdHomeRun.__name__: \
        (driverhdhomerun.DriverHdHomeRun, driverhdhomerun.DeviceHdHomeRun) }
