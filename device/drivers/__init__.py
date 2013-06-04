from device.drivers import driverdevicefile
from device.drivers import driverhdhomerun

available_drivers = \
    { driverdevicefile.DriverDeviceFile.__name__: \
        (driverdevicefile.DriverDeviceFile, driverdevicefile.DeviceFileDevice),
      driverhdhomerun.DriverHdHomeRun.__name__: \
        (driverhdhomerun.DriverHdHomeRun, driverhdhomerun.DeviceHdHomeRun) }
