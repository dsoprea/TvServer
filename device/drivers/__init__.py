from device.drivers import driverdevicefile
from device.drivers import driverhdhomerun

available_drivers = [(driverdevicefile.DriverDeviceFile, 
                      driverdevicefile.DeviceFileDevice),
                     (driverhdhomerun.DriverHdHomeRun, 
                      driverhdhomerun.DeviceHdHomeRun)]
