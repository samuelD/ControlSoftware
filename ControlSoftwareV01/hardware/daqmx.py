# import system libraries

ao = None
do = None

import ctypes
import numpy
import threading
import time
import os

try:
    from .. core import utils
except ValueError,ImportError:
    import sys
    sys.path.append(os.path.join(os.path.split(os.path.split(__file__)[-2])[-2],"core"))
    import utils
    #import pdb
    #pdb.set_trace()
# load any DLLs
nidaq = ctypes.windll.nicaiu # load the DLL

##############################
# Setup some typedefs and constants
# to correspond with values in
# C:\Program Files\National Instruments\NI-DAQ\DAQmx ANSI C Dev\include\NIDAQmx.h
# the typedefs
int32 = ctypes.c_long
uInt32 = ctypes.c_ulong
uInt64 = ctypes.c_ulonglong
float64 = ctypes.c_double
TaskHandle = uInt32
# the constants
DAQmx_Val_Cfg_Default = int32(-1)
DAQmx_Val_Volts = 10348
DAQmx_Val_Rising = 10280
DAQmx_Val_FiniteSamps = 10178
DAQmx_Val_ContSamps = 10123
DAQmx_Val_GroupByChannel = 0
DAQmx_Val_ChanForAllLines = 1
DAQmx_Val_GroupByScanNumber = 1

DAQmx_Val_RSE = 10083
DAQmx_Val_Cfg_Default = int32(-1)
DAQmx_Val_Volts = 10348
DAQmx_Val_ContSamps = 10123

#DAQmx_SampTimingType
#DAQmx_Val_OnDemand
##############################

digitalOutputs = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,24,25,26,27,28,29,30,31]

invertedChannels = [11,12,13,14,15,27,28,29,30,31]

devName = "cDAQ1Mod7"
devAO = "cDAQ1Mod4"
devAI = "cDAQ1Mod2"
#nidaq.DAQmxResetDevice(devName)
#nidaq.DAQmxResetDevice(devAO)

logTask = "c:/He3Control/logDaqmxTasks.txt"
logAOvalues = os.path.join(utils.path.getSourceDir(),"AOvalues.txt")


def checkForLogFileAOvalues():
    if os.path.exists(logAOvalues):
        return 
    else:
        numpy.savetxt(logAOvalues,numpy.zeros(16))
        
        
checkForLogFileAOvalues()



nTask = 0



class DaqmxTask(threading.Thread):
    @classmethod
    def clearAllTasks(cls):
        try:
            with open(logTask) as f:
                th = TaskHandle( 0 )
                l = f.readline()
                while l != "":
                    th = TaskHandle(int(l)) 
                    cls.CHK(nidaq.DAQmxClearTask(th))
                    l = f.readline()
            with open(logTask,"w") as f:
                pass
        except IOError:
            pass
    
    @classmethod
    def recordTaskHandle(cls,th):
        with open(logTask,"a") as f:
            f.write(str(int(th.value))+ "\n")
            
    def __init__(self,chanAddress):
        global nTask 
        self.running = True
        self.chanAddress = chanAddress
        self.taskHandle = TaskHandle( 0 )
    
        self.CHK(nidaq.DAQmxCreateTask("",ctypes.byref( self.taskHandle )))
        
        self.recordTaskHandle(self.taskHandle)
        threading.Thread.__init__( self )
        
    @classmethod
    def CHK( cls, err ):
        """a simple error checking routine"""
        if err < 0:
            buf_size = 100
            buf = ctypes.create_string_buffer('\000' * buf_size)
            nidaq.DAQmxGetErrorString(err,ctypes.byref(buf),buf_size)
            raise RuntimeError('nidaq call failed with error %d: %s'%(err,repr(buf.value)))
        if err > 0:
            buf_size = 100
            buf = ctypes.create_string_buffer('\000' * buf_size)
            nidaq.DAQmxGetErrorString(err,ctypes.byref(buf),buf_size)
            raise RuntimeError('nidaq generated warning %d: %s'%(err,repr(buf.value)))
    def startTask( self ):
        counter = 0
        self.CHK(nidaq.DAQmxStartTask( self.taskHandle ))
        
    def stopTask( self ):
        self.running = False
        nidaq.DAQmxStopTask(self.taskHandle)
        nidaq.DAQmxClearTask(self.taskHandle)
        
DaqmxTask.clearAllTasks()
class AItask(DaqmxTask):
    def __init__(self,ch,length,sampleRate):
        self.length = length
        chanAd = devAI+"/ai%i"%ch
        DaqmxTask.__init__(self,chanAd)
        
        self.CHK(nidaq.DAQmxCreateAIVoltageChan(self.taskHandle,
                                   self.chanAddress,
                                   "",
                                   DAQmx_Val_Cfg_Default,
                                   float64(-10.0),
                                   float64(10.0),
                                   DAQmx_Val_Volts,
                                   None))
        clockSource = ctypes.create_string_buffer('OnboardClock')
        self.CHK(nidaq.DAQmxCfgSampClkTiming(self.taskHandle,clockSource,float64(sampleRate),
        DAQmx_Val_Rising,DAQmx_Val_ContSamps,uInt64(length)))
        
        self.CHK(nidaq.DAQmxCfgInputBuffer(self.taskHandle,length))
        #self.sampleRate = sampleRate
        #self.periodLength = length
        
        
        
    def readValues(self):
        n = self.length
        bufferSize = uInt32(n)
        timeout = float64(10.0)
        pointsToRead = bufferSize
        pointsRead = uInt32()
        data = numpy.zeros((n,),dtype=numpy.float64)
        self.CHK(nidaq.DAQmxReadAnalogF64(self.taskHandle,pointsToRead,timeout,
                DAQmx_Val_GroupByScanNumber,data.ctypes.data,
                uInt32(2*bufferSize.value),ctypes.byref(pointsRead),None))
    
        #print "Acquired %d pointx(s)"%(pointsRead.value)
    
        return data    
        
             
class AOtask(DaqmxTask):
    def __init__(self,ch,length,sampleRate,continuous = False):
        chanAd = devAO+"/ao%i"%ch
        DaqmxTask.__init__(self,chanAd)
        self.sampleRate = sampleRate
        self.periodLength = length
        
        self.CHK(nidaq.DAQmxCreateAOVoltageChan( self.taskHandle,
                                   self.chanAddress,
                                   "",
                                   float64(-10.0),
                                   float64(10.0),
                                   DAQmx_Val_Volts,
                                   None))
        if continuous:
            timing = DAQmx_Val_ContSamps
        else:
            timing = DAQmx_Val_FiniteSamps
        self.CHK(nidaq.DAQmxCfgSampClkTiming( self.taskHandle,
                                "",
                                float64(self.sampleRate),
                                DAQmx_Val_Rising,
                                timing,
                                uInt64(self.periodLength)));
    
    
#    def __init__(self,ch,length,sampleRate):
#        chanAd = devAO+"/ao%i"%ch
#        DaqmxTask.__init__(self,chanAd)
#        self.sampleRate = sampleRate
#        self.periodLength = length
        
#        self.CHK(nidaq.DAQmxCreateAOVoltageChan( self.taskHandle,
#                                   self.chanAddress,
#                                   "",
#                                   float64(-10.0),
#                                   float64(10.0),
#                                   DAQmx_Val_Volts,
#                                   None))
#        self.CHK(nidaq.DAQmxCfgSampClkTiming( self.taskHandle,
#                                "",
#                                float64(self.sampleRate),
#                                DAQmx_Val_Rising,
#                                DAQmx_Val_FiniteSamps,
#                                uInt64(self.periodLength)));
        
         ##############################
         #self.CHK(nidaq.DAQmxWriteAnalogF64(self.taskHandle,
         #                     int32(self.periodLength),
         #                     0,
         #                     float64(-1),
         #                     DAQmx_Val_GroupByChannel,
         #                     self.data.ctypes.data,
         #                     None,None))
       
    def writeWaveform(self,waveform):
        self.data = numpy.array(waveform,dtype = numpy.float64)#numpy.zeros( ( self.periodLength, ), dtype=numpy.float64 )
        self.CHK(nidaq.DAQmxWriteAnalogF64(self.taskHandle,
                              int32(self.periodLength),
                              0,
                              float64(-1),
                              DAQmx_Val_GroupByChannel,
                              self.data.ctypes.data,
                              None,None))


class DOtask(DaqmxTask):
    def __init__(self, ch,invertedChannel = None):
      
        self.inverted = invertedChannel
        if invertedChannel is None:
            self.inverted = 0 # numpy.zeros(chmax-chmin +1,dtype = numpy.int8)
        
        chanAd = devName+"/port0/line%i"%ch
        
        DaqmxTask.__init__(self,chanAd)
        
       # self.sampleRate = sampleRate
       # self.periodLength = len( waveform )
        #numpy.zeros( ( self.periodLength, ), dtype=numpy.float64 )
        # convert waveform to a numpy array
 #       for i in range( self.periodLength ):
 #           self.data[ i ] = waveform[ i ]
        
        self.CHK(nidaq.DAQmxCreateDOChan( self.taskHandle,
                                   self.chanAddress,
                                   "",
                                   DAQmx_Val_GroupByChannel))#DAQmx_Val_ChanForAllLines))
  
        self.nWritten = int32(0)
        
        
        #self.CHK(nidaq.DAQmxSetTimingAttribute(self.taskHandle,DAQmx_SampTimingType,DAQmx_Val_OnDemand)
        
#        self.CHK(nidaq.DAQmxCfgSampClkTiming( self.taskHandle,
#                                "",
#                                float64(self.sampleRate),
#                                DAQmx_Val_Rising,
#                                DAQmx_Val_FiniteSamps,
#                                uInt64(self.periodLength)));
        
        self.CHK(nidaq.DAQmxStartTask( self.taskHandle ))
        
#        self.pattern = numpy.zeros(chMax-chMin+1,dtype = numpy.int8)
   
    def getPattern(self,val):
        return numpy.array((val+self.inverted)%2,dtype = numpy.int8)
    
    def writePulse(self):
        data = numpy.array([0,1,0],dtype = numpy.int8)
        self.CHK(nidaq.DAQmxWriteDigitalLines(self.taskHandle,
                                   int32(3),#nSamples
                                   int32(1),#autostart
                                   int32(10),#timeout
                                   DAQmx_Val_GroupByChannel,#groupBy
                                   None,###??????? don't ask me!!!
                                   data.ctypes.data,#self.pattern.ctypes.data,
                                   ctypes.byref(self.nWritten),
                                   None
                                   ))
    
    def writePattern(self,val):
        data = self.getPattern(val)
        self.CHK(nidaq.DAQmxWriteDigitalLines(self.taskHandle,
                                   int32(1),#nSamples
                                   int32(1),#autostart
                                   int32(10),#timeout
                                   DAQmx_Val_GroupByChannel,#groupBy
                                   None,###??????? don't ask me!!!
                                   data.ctypes.data,#self.pattern.ctypes.data,
                                   ctypes.byref(self.nWritten),
                                   None
                                   ))
    def readChannel(self):
        self.nRead = int32(0)
        self.nRead2 = int32(0)
        data = numpy.array([0],dtype = numpy.int8)
        self.CHK(nidaq.DAQmxReadDigitalLines(self.taskHandle,
                                   int32(1),#nSample
                                   int32(10),#timeout
                                   DAQmx_Val_GroupByChannel,#groupBy
                                   None,###??????? don't ask me!!!
                                   data.ctypes.data,#self.pattern.ctypes.data,
                                   int32(1),
                                   ctypes.byref(self.nRead),
                                   ctypes.byref(self.nRead2),
                                   None
                                   ))
        return (data[0]+self.inverted)%2
            
    def setCh(self,val):
        #self.pattern[ch] = val
        self.writePattern(val)
 

class AI:
    def __init__(self):
        pass
    
    def readValues(self,ch,n = 1,samplerate = 100):
        if n<=0:
            return
        if n==1:
            nPoints = 2
        task = AItask(ch,nPoints,samplerate)
        ret = task.readValues()
        task.stopTask()
        if n == 1:
            ret = ret[0]
        return ret
    
                                   
class AO:
    def __init__(self):
        self.lastValue = None
        self.task = [None]*16
        #self.chTask = range(16)
        #for i in range(16):
          #  self.chTask[i]=AOtask(i,1)
        
#    def waveform(self,ch,waveform,samplerate = 1000):
#        if len(waveform) == 0:
#            return
#        if len(waveform) == 1:
#            val = waveform[0]
#            waveform = [val,val]
        
        #self.taskRunning[ch] = True
        
#        self.task[ch] = AOtask(ch,len(waveform),samplerate)
#        self.task[ch].writeWaveform(waveform)
#        self.task[ch].startTask()
#        self.task[ch].CHK(nidaq.DAQmxWaitUntilTaskDone(self.task[ch].taskHandle,float64(-1)))
#        self.task[ch].stopTask()

    def waveform(self,ch,waveform,samplerate = 1000,continuous = False):
        if len(waveform) == 0:
            return
        if len(waveform) == 1:
            val = waveform[0]
            waveform = [val,val]
        
        #self.taskRunning[ch] = True
        
        self.task[ch] = AOtask(ch,len(waveform),samplerate,continuous)
        self.task[ch].writeWaveform(waveform)
        self.task[ch].startTask()
        if(continuous):
            return
        self.task[ch].CHK(nidaq.DAQmxWaitUntilTaskDone(self.task[ch].taskHandle,float64(-1)))
        self.task[ch].stopTask()

    
    def setLastValue(self,ch,val):
        sourceDir = utils.path.getSourceDir()
        if self.lastValue == None:
            self.lastValue = numpy.loadtxt(logAOvalues)
        self.lastValue[ch] = val
        numpy.savetxt(logAOvalues,self.lastValue)
        
        
    
    def getLastValue(self,ch):
        if self.lastValue == None:
            sourceDir = utils.path.getSourceDir()
            self.lastValue = numpy.loadtxt(logAOvalues)
        return self.lastValue[ch]
    
    
    def setCh(self,ch,val,slowly = True,slewRate = 0.5,sampleRate = 5000):
        """the slew rate is in V/s"""
        
        if slowly:
            lastVal = self.getLastValue(ch)
            waveform = numpy.arange(lastVal,val,slewRate/sampleRate*numpy.sign(val-lastVal)) #0.0001*
        else:
            waveform = [val,val]
        self.waveform(ch,waveform,samplerate = sampleRate)
        self.setLastValue(ch,val)
        #self.values[ch]=val
    
        
        #except AttributeError:
        #    raise ValueError("requested channel is not an output")
        #if ch in range(0,8):
        #    self.ch0to7.setCh(ch-0,val)
        #if ch in range(8,16):
        #    self.ch8to15.setCh(ch-8,val)
        #if ch in range(24,32):
        #    self.ch24to31.setCh(ch-24,val)
        
       
    def getCh(self,ch):
        return self.chTask[ch].readChannel()




class DO:
    def __init__(self):
        self.chTask = range(32)
        for i in digitalOutputs:
            self.chTask[i]=DOtask(i,invertedChannel = (i in invertedChannels))
            
        #self.ch0to7  = DOtask(0,7,invertedChannels = invertedChannels0to7)
        #self.ch8to15 = DOtask(8,15,invertedChannels = invertedChannels8to15)
        #self.ch24to31 = DOtask(24,31,invertedChannels = invertedChannels24to31)
       
    def pulseCh(self,ch):   
        try:
            self.chTask[ch].writePulse()
        except AttributeError:
            raise ValueError("requested channel is not an output")
        
    def setCh(self,ch,val):
        try:
            self.chTask[ch].setCh(val)
        except AttributeError:
            raise ValueError("requested channel is not an output")
        #if ch in range(0,8):
        #    self.ch0to7.setCh(ch-0,val)
        #if ch in range(8,16):
        #    self.ch8to15.setCh(ch-8,val)
        #if ch in range(24,32):
        #    self.ch24to31.setCh(ch-24,val)
       
    def getCh(self,ch):
        return self.chTask[ch].readChannel()
try:
    ao = AO()
    do = DO()
    ai = AI()
except RuntimeError:
    print "could not create ao or do"




#shutterNames = {"TiSa":11,"diode":12,"LO":13,"detector":14,"signal":15}
#dangerous = {"TiSa":True,"diode":False,"LO":False,"detector":False,"signal":True}
#shutterNames = {"TiSa":11,"diode":12,"LO":13,"detectorPlus":14,"detectorMinus":27,"signal":15}
#dangerous = {"TiSa":True,"diode":False,"LO":False,"detectorPlus":False,"detectorMinus":False,"signal":True}
shutterNames = {"TiSa":11,"diode1":12,"LO":13,"detectorPlus":14,"detectorMinus":27,"signal":15,"diode2":29}
dangerous = {"TiSa":True,"diode1":False,"LO":False,"detectorPlus":False,"detectorMinus":False,"signal":True,"diode2":False}

def setShutters(name = "", confirmDangerous = True):
#    """available positions : diode, homodyne, homodyneDiode"""
    spectroDiodeDict = {"diode1":0,"diode2":1,"TiSa":1,"LO":1,"detectorMinus":1,"detectorPlus":0,"signal":0}
    homoDict = {"diode1":1,"diode2":1,"TiSa":0,"LO":0,"detectorMinus":0,"detectorPlus":0,"signal":0}
    homoDiodeDict = {"diode1":0,"diode2":1,"TiSa":1,"LO":0,"detectorMinus":0,"detectorPlus":0,"signal":0}
    adjustBalancedDetectors = {"diode1":1,"diode2":1,"TiSa":0,"LO":0,"detectorMinus":0,"detectorPlus":0,"signal":1}
    spectroDiodeAndTiSa = {"diode1":0,"diode2":1,"TiSa":0,"LO":1,"detectorMinus":1,"detectorPlus":0,"signal":0}
    shutAll = {"diode1":1,"diode2":1,"TiSa":1,"LO":1,"detectorMinus":1,"detectorPlus":1,"signal":1}
    pos = {"diodeAndTiSa":spectroDiodeAndTiSa,"spectroDiode":spectroDiodeDict,"homodyne":homoDict,"homodyneDiode":homoDiodeDict,"balanceDetectors":adjustBalancedDetectors,"shutAll":shutAll}
    
    if name == "":
        seq = [(a,b) for (a,b) in zip(range(len(pos)),pos.keys())]
        n = raw_input("available positions are" + str(seq) + "enter a number:")
        name = seq[int(n)][1]
    try:
        setShuttersFromDict(pos[name],confirmDangerous = confirmDangerous)
    except KeyError:
        print "available positions for shutters are %s"%pos.keys() 


def setShutter(name = "",val = -1,confirmDangerous = True):
    if name == "":
        seq = [(a,b) for (a,b) in zip(range(len(shutterNames)),shutterNames.keys())]
        n = raw_input("available shutters are" + str(seq) + "enter a number:")
        name = seq[int(n)][1]
    try:
        num = shutterNames[name]
    except KeyError:
        print "available shutters are %s"%shutterNames.keys()
    if val == -1:
        state = getShutter(name)
        
        if(name=="diode2"):    # invert open-close for diode2, due to peculiar space constraints where it is mounted on table
            state=not state
            
        yn = raw_input("shutter " + name + " is currently " + "%s"%{0:"open",1:"closed"}[state] + ". do you want to %s it?(y/n)"%{1:"open",0:"close"}[state])
        if yn!="y":
            return
        else:
            confirmDangerous = False
            val = abs(state-1)

    if val==0 and confirmDangerous and dangerous[name]:
        if getShutter(name)==1:
            yn = raw_input("shutter %s is currently closed, do you really want to open it (y/n)?"%name)
            if yn != "y":
                raise ValueError("user forbid me to open shutter %s"%name)
    do.setCh(shutterNames[name],val)
    
    
    
def setShuttersFromDict(d,confirmDangerous = True):
    for s in d.iteritems():
        setShutter(s[0],s[1],confirmDangerous = confirmDangerous)
#def setShutters(name = ""):
##    """available positions : diode, homodyne, homodyneDiode"""
#    spectroDiodeDict = {"diode":0,"TiSa":1,"LO":1,"detector":1,"signal":0}
#    homoDict = {"diode":1,"TiSa":0,"LO":0,"detector":0,"signal":0}
#    homoDiodeDict = {"diode":0,"TiSa":1,"LO":0,"detector":0,"signal":0}
#    adjustBalancedDetectors = {"diode":1,"TiSa":0,"LO":0,"detector":0,"signal":1}
#    spectroDiodeAndTiSa = {"diode":0,"TiSa":0,"LO":1,"detector":1,"signal":0}
#    shutAll = {"diode":1,"TiSa":1,"LO":1,"detector":1,"signal":1}
#    pos = {"diodeAndTiSa":spectroDiodeAndTiSa,"spectroDiode":spectroDiodeDict,"homodyne":homoDict,"homodyneDiode":homoDiodeDict,"balanceDetectors":adjustBalancedDetectors,"shutAll":shutAll}
    
#    if name == "":
#        seq = [(a,b) for (a,b) in zip(range(len(pos)),pos.keys())]
#        n = raw_input("available positions are" + str(seq) + "enter a number:")
#        name = seq[int(n)][1]
#    try:
#        setShuttersFromDict(pos[name])
#    except KeyError:
#        print "available positions for shutters are %s"%pos.keys() 


def getShutter(name = ""):
    try:
        return do.getCh(shutterNames[name])
    except KeyError:
        print "available shutters are %s"%shutterNames.keys()
        
def getShutters():
    d = dict()
    dVisual = dict()
    
    for name in shutterNames:
        val = getShutter(name)
        d[name] = val
        if val == 1:
            ext = "     "
        else:
            ext = "-----"
        dVisual[name] = str(getShutter(name)) + ext
    t = """
       TiSa -----%(TiSa)s\        /----------LO---%(LO)s\       /-%(detectorPlus)sDet+
                        \      /                       >-----< 
                         >----/----%(signal)s---CRYO------/       \-%(detectorMinus)sDet-
                        /
        diode----%(diode)s/      
    """%dVisual
    print t
    return d

def PWM_single(duty_cycle = 0.075, n = 500):
    if (duty_cycle>1.0)|(duty_cycle<0.0):
        raise ValueError("Duty cycle beyond bounds")
        return
             
    a=numpy.zeros(n)
    len_ON=int(round(n*duty_cycle))
    a[0:len_ON]=numpy.ones(len_ON)
    return a

def PWM_sweep(duty_cycle_start = 0.05, duty_cycle_stop = 0.1, steps = 26, n = 500):
    a=numpy.zeros(steps*n)
    dc=numpy.linspace(duty_cycle_start,duty_cycle_stop,steps)
    for i in range(steps):
        a[(i*n):((i+1)*n)]=PWM_single(duty_cycle = dc[i], n=n)
    return a


def move_in(ch=3, inpos=0):
    """moves powermeter into beam"""
    movein=PWM_sweep(0.05+inpos*.05,0.05+inpos*.05,26)
    ao.waveform(ch,5*movein,25000,False)

def move_out(ch=3, outpos=1):
    """moves powermeter into beam"""
    moveout=PWM_sweep(0.05+outpos*.05,0.05+outpos*.05,26)
    ao.waveform(ch,5*moveout,25000,False)

def flip_and_measure(ch=3,inpos=0,outpos=1):
    from .. import defaultDevice
    from .. import W
    import time
    p=defaultDevice("POWER2")
    move_in(ch,inpos)
    
    print('Measuring Power...')
    check=1
    powerold=-10*W
    pwr=1*W
    while (abs(powerold-pwr)/abs(pwr)>.05):
        powerold=pwr
        time.sleep(0.050)
        pwr=p.getPower()
        print(pwr.asNumber())
        
        if pwr<100E-9*W:
            break
        
    print('done')
    
    move_out(ch,outpos)
    return pwr

try:
    from ..GUI import Qt_AOControl
except ValueError as e:
    print e
else:
    aoControl = Qt_AOControl.Qt_AOControl(setPoint = ao.getLastValue(0))
    aoControl.show()


