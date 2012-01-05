print "init hardware"
try:
    import daqmx
except WindowsError:
    daqmx = None
import devices,hardwareDevices
from hardwareDevices import detectHardwareForDefault
__ALL__ = ["daqmx","devices","hardwareDevices","detectHardwareForDefault"]