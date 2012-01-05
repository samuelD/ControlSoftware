from devices import *
import struct
#import readConfig
#import Spectrum
import numpy
from ..core import utils
from ..core.utils import Unit
from ..core.utils.Unit import deg,Hz,inUnit,m,mA,mHz,MHz,nm,s,V,dBm,Veff2dBm
#from ..core.utils.misc import Veff2dBm
from ..core.utils import readConfig
from .. import W
##########################################################################
###  a decorator function to add a device type in the autodetect list  ###
##########################################################################
def registerDevice(defaultName, IDNstring):
    """The IDNstring is all the second string after the comma returned by the *IDN? visa command"""
    global byModelName
    
    def theDecorator(deviceClass):
        global byModelName
        name = defaultName
        redun = 1
        while(byModelName.has_key(name)):
            redun+=1
            name = defaultName + "_" + str(redun)    
        byModelName[IDNstring] = (deviceClass,name)
        return deviceClass
    return theDecorator

byModelName = dict()


class DeviceParaRS(DevicePara):
    def getValue(self):
        """Rhode Schwarz returns first the name of the parameter, it has to be removed"""
        self.device.ask("%s?"%(self.visaName)).split()[1]

class DeviceNumParaRS(DeviceNumPara,DeviceParaRS):
    pass
@registerDevice("FreqGen","SMY01")
class RhodeSchwarzSMY01(FreqGen,VisaDevice):
    """well... you probably got it?"""
    def __init__(self,adr = ""):
        VisaDevice.__init__(self,adress = adr,paraClass = DeviceParaRS, numParaClass = DeviceNumParaRS)
        self.setNumParam("frequency","RF",100,MHz,[0.009,1040.0])
        self.setNumParam("Veff","level",.100,V,[2.25e-8,1.997])
        self.setNumParam("Power","level",0,dBm,[-140,19])


@registerDevice("NA","E5061B")
class AgilentE5061B(NetworkAnalyzer,VisaDevice):
    """well... you probably got it?"""
#    def setNumParam(self,parName,*args):
#        """uses the parameters dedicated for one channel"""
#        self.numParams[parName] = DeviceNumParaNoUnits(self,*args)

    def __init__(self,adr = ""):
        VisaDevice.__init__(self,adress = adr,numParaClass = DeviceNumParaNoUnits)
        NetworkAnalyzer.__init__(self)
        self.setChParam("start","sens%d:freq:star",1e6,Hz,[5,3e9])
        self.setChParam("stop","sens%d:freq:stop",200e6,Hz,[5,3e9])
        self.setChParam("span","sens%d:freq:span",200e6,Hz,[5,3e9])
        self.setChParam("center","sens%d:freq:center",150e6,Hz,[5,3e9])
        self.setChParam("RBW","sens%d:band", 1e3,Hz,[1,3e5])
        self.setChParam("averages","sens%d:aver:coun",1,m/m,[1,999])
        self.setChParam("points","sens%d:SWE:POIN",1601,m/m,[1,1601])
        
       # self.setChParam("power",":SOURCE1:POWER?",1601,m/m,[1,1601])
        
        
        self.setNumParam("frequency","freq",100,Hz,[5,3e9])
        self.setNumParam("Power",":source1:power:level:imm:ampl",0,dBm,[-45,10])
        self.write(":form:data real32")
        self.write(":sens1:aver 1;:sens2:aver 1;:sens3:aver 1;:sens1:aver 4")
        #self.write(":sens1:bwa;:sens2:bwa;:sens3:bwa;:sens4:bwa;")
        
    def setStateFromDict(self,d):
        self.write(":mmem:load \"%s.sta\""%d["name"])
    
    def saveStateOnDevice(self,name):
        self.write(":mmem:stor \"%s.sta\""%name)
    
    def setOutputOn(self,bool = True):
        d = {True:"output on",False:"output off"}
        self.write(d[bool])
    
    #def saveStateToDict(self,name = ""):
    #    return {"filename":name}
    
    def trigger(self):
        self.write(":INIT1:IMM") #trigger single trace
    
    
    def getWinName(self):
        if self.getFormat() == "PHAS":
            return self.__defaultName__ + "_PHASE"
        else:
            return self.__defaultName__
    def getPower(self):
        return float(self.ask(":SOURCE1:POWER?"))*Unit.dBm
    
    def _getXaxis_(self):
        if float(self.ask("sens:freq:span?"))!=0:
            f = self.ask(":sens%d:freq:data?"%self.getChannel())
            return self._parseStrIntoArray_(f)
        else:
            nPoints   = int(self.ask(":sens:sweep:points?\r"))
            tStart = 0
            tStop = float(self.ask(":sens1:sweep:time?"))
            Xincr = (tStop-tStart)/(nPoints-1)
            Xzero = tStart
            return numpy.arange(Xzero,Xzero+nPoints*Xincr-Xincr/2,Xincr)            
        
        
    def autoscale(self):
        self.write("disp:wind1:trac1:Y:auto")
        
    def _setRBWAuto_(self):
        self.write(":sens%d:bwa"%self.getChannel())
    
 #   def recallState(self, state):
 #       val=[]
 #       try: 
 #           val = int(state)
 #           val = "\"D:/state0"+str(val)+".sta\""
 #       except ValueError:
 #           val = "\"D:/"+state+".sta"+"\""
 #       self.write(":mmem:load %s"%val)
       

 #   def saveState(self, state):
 #       try: 
 #           val = int(state)
 #           val = "\"state0"+str(val)+".sta\""
 #       except ValueError:
 #           val = "\""+state+".sta"+"\""
 #       self.write(":mmem:stor %s"%val)
        
    def _getYvalues_(self):
        y = self.ask(":calc%d:data:fdat?"%self.getChannel())
        ynum=self._parseStrIntoArray_(y)
        return ynum[0::2]
    def _avgClear_(self):
        self.write("sens%d:aver:cle"%self.getChannel())    
    
    def setCurrTrace(self,tr):
        self._currentTr_ = tr
        self._setActiveTrace_()
    
    def getFormat(self):
        """returns the format for the current trace"""
        return self.ask(":CALC1:FORMAT?")    
        
    def _getCurrTrace_(self):
        return self._currentTr_        
    
    def _setActiveTrace_(self):
        self.write(":CALC%d:PAR%d:SEL"%(self.getChannel(),self._getCurrTrace_()))
    
    def ActivateChannels(self,no=1):
        """Takes integer out of [1,4] to display 1,2,3 or 4 channels. This is 
        required if you want to use the corresponding channel"""
        if 0<int(no)<5 :
            if int(no)==1 : 
                self.write("disp:spl D1")
            if int(no)==2 : 
                self.write("disp:spl D12")
            if int(no)==3 : 
                self.write("disp:spl D123")
            if int(no)==4 : 
                self.write("disp:spl D1234")
        else:
            raise ValueError("Only one number out of [1,2,3,4] is allowed")
        
    def ActivateTraces(self,no=1):
        """Takes integer out of [1,4] to display 1,2,3 or 4 traces. This is 
        required if you want to use the corresponding trace"""
        if 0<int(no)<5 :
            self.write("calc%d:par:coun %d"%(self.getChannel(),no))
            if int(no)==1 : 
                self.write("disp:wind%d:spl D1"%(self.getChannel()))
            if int(no)==2 : 
                self.write("disp:wind%d:spl D1_2"%(self.getChannel()))
            if int(no)==3 : 
                self.write("disp:wind%d:spl D1_2_3"%(self.getChannel()))
            if int(no)==4 : 
                self.write("disp:wind%d:spl D1_2_3_4"%(self.getChannel()))
        else:
            raise ValueError("Only one number out of [1,2,3,4] is allowed")
        
    def _initDataTransfer_(self):
        return
        
    def _setVeff_(self,Veff):
 #       super(RhodeSchwarzSMY01, self).checkForBounds(Veff2dBm(Veff))
        self.setPower(Veff2dBm(Veff))

    def _setPower_(self,Power):
        """Power in dBm without unit on Port 1"""
#        super(AgilentE5061B, self).checkPowerForBounds(Power)
        self.write((":SOURCE1:POWER %f")%(Power))

    def _setFreq_(self,freq): #that's actually where the job should be done
#        super(AgilentE5061B, self).checkFreqForBounds(freq)
        self.write("SENS%d:FREQ:CENTER %f"%(self.getChannel(),inUnit(freq,Hz)))
        self.write("SENS%d:FREQ:SPAN 0"%self.getChannel())

    def _getYmathParams_(self):
        gain = 1
        offset = 0
        return (gain,offset)

    def _getXmathParams_(self):
        nPoints   = int(self.ask(":sens%d:sweep:points?\r"%self.getChannel()))
        freqStart = float(self.ask(":sens%d:frequency:start?\r"%self.getChannel())) 
        freqStop  = float(self.ask(":sens%d:frequency:stop?\r"%self.getChannel())) 
        Xincr = (freqStop-freqStart)/(nPoints-1)
        Xzero = freqStart
        return (Xincr,Xzero)
#    ":trace:data? trace%i"%traceNr
    

    def _parseStrIntoArray_(self,trace):
        offset = int(trace[1])+2
        dt = numpy.dtype(numpy.float32)
        dt = dt.newbyteorder('>')
        return numpy.frombuffer(trace, dtype=dt, offset = offset).astype(numpy.float64)
    
@registerDevice("SCOPE","DPO4034")
class DPO4034(Scope,VisaDevice):
    
#    def setNumParam(self,parName,*args):
#        """sends parameters without the units in the visa string"""
#        self.numParams[parName] = DeviceNumParaNoUnits(self,*args)

    def __init__(self,adr):
        VisaDevice.__init__(self,adress = adr,numParaClass = DeviceNumParaNoUnits)
        Scope.__init__(self)
    
        self.setNumParam("t_div","horizon:scale",1e-3,s,[1e-9,400])
        self.setChParam("V_div","ch%d:Scale",1.0,V,[1e-3,10])
        self.setNumParam("nSamples","level",0,dBm,[-140,19])

    def _getYvalues_(self):
        y = self.ask("curve?")
        ynum=self._parseStrIntoArray_(y)
        del y
        return ynum  
    
    def _getXaxis_(self):
        nPoints   = int(self.ask("WFMOutpre:NR_Pt?"))
        Xincr = float(self.ask("WFMOutpre:Xincr?"))
        Xzero = float(self.ask("WFMOutpre:XZero?"))
        return numpy.arange(Xzero,Xzero+nPoints*Xincr-Xincr/2,Xincr)

    def _getTraceObject_(self,X,Y,**kwds):
        """asssumes X is in Hertz and Y in dBm"""
        from ..core import Spectrum
        return Spectrum.traceLin(X,Y,unit_x = s,unit_y = V,**kwds)    
    
    def _initDataTransfer_(self):
        self.write("DATa:ENCdg RPBinary")
        bNr = 1
        self.write("WFMOutpre:BYT_Nr %i"%bNr)

## waveform
        self.write("data:start 1")
        rl = self.ask("horizontal:recordLength?")
        self.write("data:stop %s"%rl)
        return
    
    def _setCurrentChannelForTrace_(self):
        self.write("data:source CH%i"%self.getChannel())
        
    def _getYmathParams_(self):
        mult = float(self.ask("WFMOutpre:YMUlt?"))
        offset =  float(self.ask("WFMOutpre:YOFf?"))
        return (mult,offset)
    
    
    def _getXmathParams_(self):
        Xincr = float(self.ask("WFMOutpre:Xincr?"))
        Xzero = float(self.ask("WFMOutpre:XZero?"))
        return (Xincr,Xzero)

    def setPosition(self,position):
        self.write("ch%i:Position %f"%(self.getChannel(),position))
    def getPosition(self):
        return float(self.ask("ch%i:Position?"%self.getChannel()))

    def triggerAndWait(self):
        """triggers single acquisition and waits until acquisition finished"""
        self.write("ACQ:STOPA SEQ")
        self.write("ACQ:State RUN")
        while int(self.ask("ACQ:State?")):
            import time
            time.sleep(0.02)

    def _autoScale_(self, keepTrace=False):
        """rescales trace to fit y-range; sets position to zero and does not act on it"""
        self.setPosition(0.0) #center trace
        self.write("ch%i:Offset 0.0"%self.getChannel())
        done=False
        f=0.0
        actions=""
        while done==False:
            self.triggerAndWait()
            data=self._getYvalues_()
            if ((max(data)==253) | (min(data)==2)):
                a=self.getV_div().asNumber()
                f=a*8.0
                try:
                    self.setV_div(f*V)
                except ValueError:
                    done=True
                actions=actions+"> "
            elif ((max(data)<168) & (min(data)>88)):
                fplus=128.0/abs(max(data)-128)
                fminus=128.0/abs(128.0-min(data))
                a=self.getV_div().asNumber()
                f=a/(min([fplus, fminus])*.6)
                try:
                    self.setV_div(f*V)
                except ValueError:
                    done=True
                actions=actions+"< "
            else:            
                done=True
        
        actions=actions+"done"
        if keepTrace==False:
            self.write("ACQ:STOPA RUNST")
            self.write("ACQ:State RUN")
        return actions


@registerDevice("ESA","N9020A")
class MXA(ESA,VisaDevice):
    def __init__(self,adr):
        VisaDevice.__init__(self,adress = adr)
        ESA.__init__(self)
        self.write("sens:det RMS")
        self.setNumParam("start","sens:freq:star",1e6,Hz,[20,3.6e9])
        self.setNumParam("stop","sens:freq:stop",200e6,Hz,[20,3.6e9])
        self.setNumParam("span","sens:freq:span",200e6,Hz,[20,3.6e9])
        self.setNumParam("center","sens:freq:center",150e6,Hz,[20,3.6e9])
        self.setNumParam("RBW","sens:band",1e3,Hz,[1,8e6])
        self.setNumParam("averages","sens:aver:coun",100,m/m,[1,10000])
        self.setNumParam("points","sens:SWE:POIN",1001,m/m,[1,40001])
        self.setNumParam("sweeptime","sens:swe:time",1,s,[1e-3,1000])
        
        
#    def setStateFromDict(self,d):
#        self.write(":mmem:load:state \"%s.state\""%name)
#        self.write("*rcl %d"%self._multiConfig_.numFromName(name))
       
    #def saveStateOnDevice(self,name):
    #    n = self._multiConfig_.numFromName(name)
    #    self.write("*sav %d"%n)
    
    def saveStateOnDevice(self,name):
        self.write(":mmem:stor:state \"%s.state\""%name)
    
    def setStateFromDict(self,d):
        self.write(":mmem:load:state \"%s.state\""%d["name"])
        #n = self._multiConfig_.numFromName(d["name"])
        
        
    def _initDataTransfer_(self):
        self.write(":format:trace:data int,32")
    def _setAutoSweepTime_(self):    
        self.write("sens:swe:time:auto on")
    def _restart_(self):
        self.write("INIT:REST\r")

    def _getYvalues_(self):
        try:
            y = self.ask(":trace:data? trace%i"%self.getChannel())
            ynum=self._parseStrIntoArray_(y)
        except ValueError:
            print "the trace didn't contain the right number of element, trying again..."
            return self._getYvalues_()
        return ynum        
   
    def _getNPoints_(self):
        return int(self.ask(":sens:sweep:points?\r"))
         
    def _getXaxis_(self):
        nPoints   = self.getNPoints()#int(self.ask(":sens:sweep:points?\r"))
        if Unit.toSINumber(self.getSpan()) == 0:
            start = 0
            stop  = Unit.toSINumber(self.getSweepTime())
        else:
            start = Unit.toSINumber(self.getStart())#float(self.ask(":sens:frequency:start?\r")) 
            stop  = Unit.toSINumber(self.getStop())#float(self.ask(":sens:frequency:stop?\r")) 

        
        Xincr = (stop-start)/(nPoints-1)
        Xzero = start
        return numpy.arange(Xzero,Xzero+nPoints*Xincr-Xincr/2,Xincr)
   
    def _setRBWAuto_(self):
        self.write("sens:band:auto on\r")
        
    def _getSweepTime_(self):
        self.write(":swe:time?")
        
    def _getAverages_(self):
        self.write(":aver:coun?")

    def _getYmathParams_(self):
        gain = 0.001
        offset = 0
        return (gain,offset)

    def _getXmathParams_(self):
        nPoints   = int(self.ask(":sens:sweep:points?\r"))
        freqStart = float(self.ask(":sens:frequency:start?\r")) 
        freqStop  = float(self.ask(":sens:frequency:stop?\r")) 
        Xincr = (freqStop-freqStart)/(nPoints-1)
        Xzero = freqStart
        return (Xincr,Xzero)
#    ":trace:data? trace%i"%traceNr

    def _parseStrIntoArray_(self,trace):
        val = []
        offset = int(trace[1])+2
        return  numpy.frombuffer(trace,dtype = ">i",offset = offset)

 

class NewFocus6300(LaserDiode,VisaDevice):
    def __init__(self,adr):
        VisaDevice.__init__(self,adress = adr)
        LaserDiode.__init__(self)
        self.setNumParam("lambda_start",":wavelength:start",1520,nm,[1519.68,1570.70])
        self.setNumParam("lambda_stop",":wavelength:stop",1570,nm,[1519.68,1570.70])

        #self.setNumParam("lambda","sens:freq:center",150e6,Hz,[20,3.6e9])
        self.setNumParam("current","curr",10,mA,[0,149])
        self.setNumParam("forward_slew_rate","wave:slew:forw",1,m,[0.01,28])
        self.setNumParam("lambda_value",":wave",1550,nm,[1519.68,1570.70])
      
class Newport2832(VisaDevice):
    def __init__(self,adr):
        VisaDevice.__init__(self,adress = adr)
    def getPower(self, Channel):
        """takes Channel ('A' or 'B') and returns power in W"""
        return float(self.ask("R_%c?"%Channel))
    

class NewFocus6312(NewFocus6300):
    def __init__(self,adr):
        NewFocus6300.__init__(self,adr)
        self.setNumParam("lambda_start",":wavelength:start",780,nm,[764.64,781.67])
        self.setNumParam("lambda_stop",":wavelength:stop",780,nm,[764.64,781.67])
        #self.setNumParam("lambda","sens:freq:center",150e6,Hz,[20,3.6e9])
       # self.setNumParam("current","curr",10,mA,[0,149])
       # self.setNumParam("forward_slew_rate","wave:slew:forw",1,m,[0.01,28])
        self.setNumParam("lambda_value",":wave",780,nm,[764.64,781.67])


class Agilent33250A(ArbSigGen,VisaDevice):
    def __init__(self,adr):
        VisaDevice.__init__(self,adr)
        ArbSigGen.__init__(self)
        self.setNumParam("V","VOLT",1,V,[0,5]) #gives Vpp#
        self.setNumParam("V_DC","VOLT:OFFS",1,V,[0,5])
        self.setNumParam("f","FREQ",1,Hz,[0,80e6])
        
        self.setNumParam("frequency","FREQ",100,Hz,[1e-6,80e6])    
        self._storedWfm_ = utils.misc.multiConfig(self.__defaultName__)
       
    def recallWfm(self,state = -1):
        d  = self._storedWfm_.getState(state)
        self.write("FUNC:USER " + d["name"])
        self.outputArb()
        
    def outputArb(self):
        self.write("FUNC USER")
        
    def saveWfmOnDevice(self,wfmName):
        self.write("DATA:COPY " + wfmName + ", VOLATILE")
    
    def saveVolatileWfm(self,wfmName):
        d = {"name":wfmName}
        self.saveWfmOnDevice(wfmName)
        self._storedWfm_.addState(wfmName,d)   
        
    def _loadWaveform_(self,wf,samplerate,autorun):
        t = ""
        for val in wf:
            if abs(val)>1:
                raise ValueError("waveform should span between -1 and 1")
            t = t+", " + str(val)
        self.write("DATA VOLATILE" + t)
        
    def setSine(self,V = 0.1,f = 1):
        self.write("FUNC SIN")
        self.setVoltage(V)
        self.setFrequency(f)
        
    def setSquare(self,V = 0.1,f = 1):
        self.write("FUNC SQU")
        self.setVoltage(V)
        self.setFrequency(f)
               
    def setRamp(self,V = 1.3, f = 100):
        self.write("FUNC RAMP")
        self.setVoltage(V)
        self.setFrequency(f)
        
    def setDC(self,V_DC=0):
        self.write("FUNC DC") 
        self.setVoltageDC(V_DC)     

    def setOutput(self,out):
        if out:
            self.write("OUTP ON")
        else:
            self.write("OUTP OFF")
        
    def getVoltage(self):
        self.ask("VOLT?")
      
      
      
@registerDevice("AFG","AFG3102")
class AFG3102(ArbSigGen,MultiChannel,VisaDevice):    
    def __init__(self,adr):
        VisaDevice.__init__(self,adr)
        #ArbSigGenTwoCh.__init__(self)
        ArbSigGen.__init__(self)
        MultiChannel.__init__(self)
        self.setChParam("V","SOURCE%d:VOLTAGE:AMPLITUDE",1,V,[0,5])
        self.setChParam("f","SOURCE%d:FREQUENCY",1,Hz,[0,100e6])
        self.setChParam("phi","SOURCE%d:PHASE:ADJUST",0,deg,[-360,360])
       
        
        
    #def setPhase(self,Ch=1,phi=0):
    #    self.write("SOURCE"+str(Ch)+":PHASE:ADJUST "+str(phi)+"DEG")
        
    def setSine(self,V=0.2,f=1e6,phi=0):
        self.write("SOURCE%d:FUNCTION SIN"%self.getChannel())
        self.setVoltage(V)
        self.setFrequency(f)
        self.setPhase(phi)
        
    def setRamp(self,V=0.2,f=1e6,phi=0):
        self.write("SOURCE%d:FUNCTION RAMP"%self.getChannel())
        self.setVoltage(V)
        self.setFrequency(f)
        self.setPhase(phi)
        
    def setSquare(self,V=0.2,f=1e6,phi=0):
        self.write("SOURCE%d:FUNCTION SQUARE"%self.getChannel())
        self.setVoltage(V)
        self.setFrequency(f)
        self.setPhase(phi)
        
    def initPhase(self): #initialize phase lock between channels
        self.write("SOUR1:PHAS:INIT")
        
    #def getVoltage(self,Ch=1):
    #    print self.ask("SOURCE"+str(Ch)+":VOLTAGE:AMPLITUDE?")        
        
    def getFrequency(self):
        print self.ask("SOURCE%d:FREQUENCY?"%self.getChannel())
        
    def getPhase(self):
        print self.ask("SOURCE%d:PHASE?"%self.getChannel())
        
#### piezzo controller Johann
class MDT693A(VisaDevice):
    def __init__(self,adr):
        VisaDevice.__init__(self,adress = adr)
        self.instr.baud_rate = 115200
        self.write('xh75\r')
        self.write('yh75\r')
        self.write('zh75\r')
        self.write('xl0\r')
        self.write('yl0\r')
        self.write('zl0\r')
        
    def getIdentifyStr(self):
#        self.ask()
        pass

    def setX(self,val_V):
        self.write('xv' + str(val_V) + '\r')
    
    def setY(self,val_V):
        self.write('yv' + str(val_V) + '\r')
    
    def setZ(self,val_V):
        self.write('zv' + str(val_V) + '\r')
    
    def scan(self,lowY=0, highY=75, lowZ=0, highZ=75, stepY=1, stepZ=1):
        for z in range(0,(highZ-lowZ)/stepZ,2):
            self.setZ(lowZ+stepZ*z)
            time.sleep(0.1)
            for y in range(0,(highY-lowY)/stepY):
                self.setY(lowY+stepY*y)
                time.sleep(0.1)
            z=z+1
            self.setZ(lowZ+stepZ*z)
            time.sleep(0.1)
            for y in range((highY-lowY)/stepY-1,-1,-1):
                self.setY(lowY+stepY*y)
                time.sleep(0.1)      

@registerDevice("POWER","PM100D")
class ThorlabsPM100D(VisaDevice):
    def __init__(self,adr):
        VisaDevice.__init__(self,adress = adr)
    def getPower(self):
        """returns power in W"""
        return float(self.ask("measure:power?"))*W                        
        
def getAllDevices(recheck = True):
    global _allConnectedDevices_
    if (_allConnectedDevices_ == None) or recheck:
        _allConnectedDevices_ =  getAllConnectedDevices()  
    return _allConnectedDevices_

def getAllFreqGen():
    li = []
    for dev in getAllDevices(recheck = False):
        if isinstance(dev,FreqGen):
            li.append(dev)
    return li


# the dictionnary of defaultDevices
defaultDeviceDict = dict()

def defaultDevice(str):
    """for instance defaultDevice("SCOPE")->returns the hardwareDevice object"""
    global defaultDeviceDict
    (className,address) = readConfig.defaultDeviceAddress(str)
    reinit = False
    try:
        d = defaultDeviceDict[str]
        #if d.address != address:
         #   reinit = True
    except KeyError:
        reinit = True
    
    if reinit:
        try:
            defaultDeviceDict[str] = eval(className + "(\"" + address + "\")")
        except NameError as e:
            print e
            return None
    return defaultDeviceDict[str]
        
        
        
        
def detectHardwareForDefault():
    print "detecting hardware"
    try:
        l = visa.get_instruments_list()
    except NameError:
        print "no visa drivers on this machine... hardware.conf won't be edited"
        return
    fileStr = "dummyDevice = dum007@GPIB::3\n"
    for str in l:
        print str
        try:
            instr = visa.instrument(str)
            instr.timeout = 1
            ident = instr.ask("*IDN?")
        except visa.VisaIOError:
            continue
            
        try:
            type = ident.split(",")[1]
        except IndexError:
            continue
        try:
            className = byModelName[type][0].__name__
        except KeyError:
            pass
        else:
            name =  byModelName[type][1]#.defaultName()
            from ..core.utils import readConfig
            readConfig.updateHardware(name, className, str)
            #newLine =  name + " = " + className + "@" + str + "\n"
            #fileStr = fileStr + newLine
    #with open(utils.path.getHardwareFile(),"w") as f:
    #    f.write(fileStr)
        
        
        
        
def getAllConnectedDevices():
    """returns a list of all connected devices"""
    print """checking default devices connection..."""
    li = []
    allNames = readConfig.getAllHardwareNames()
    for name in allNames:
        try:
            d = defaultDevice(name)
        except (visa.VisaIOError,AttributeError):
            pass
        else:
            li.append(d)
    return li
    
    
if dummyMode is False:
    pass
    #getAllConnectedDevices()
    #for dev in defaultDeviceDict:
    #    print(dev,defaultDeviceDict[dev].getIdentifyStr())