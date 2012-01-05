dummyMode = False
try:
    import visa
    import pyvisa
except (ImportError,OSError):
    dummyMode = True


#import defaultHardware
#from Unit import *

from ..core import utils
from ..core.utils.Unit import Hz,inUnit,s
from ..core import Spectrum
import numpy
#import Spectrum
import time

verbose = False

 
     
#     = {
#"E5061B":("AgilentE5061B","NA"),
#"DPO4034":("DPO4034","SCOPE"),
#"SMY01":("RhodeSchwarzSMY01","FREQGEN"),
#"N9020A":("MXA","ESA"),
#"6328":("NewFocus6300","DIODE_LASER"),
#"2832-C":("Newport2832","PZT"),
#"33250A":("Agilent33250A","ARBGEN")
#}


class DevicePara:
    """class for parameter with default behviour"""
    def __init__(self,device,visaName):
        self.visaName = visaName
        self.device = device

    def setValue(self,str):
        self.device.write("%s %s"%(self.visaName,str))

    def getValue(self):
        return self.device.ask("%s?"%(self.visaName))

class DeviceNumPara(DevicePara):
    """a numeric parameter for a device e.g., frequency (with default behaviour)"""
    def __init__(self,device,visaName,defaultValue,defaultUnit,bounds):
        DevicePara.__init__(self,device,visaName)
        self.defaultValue = Unit.addDefaultUnit(defaultValue,defaultUnit)
        self.defaultUnit = defaultUnit
        Unit.addDefaultUnit(bounds[0],defaultUnit)
        Unit.addDefaultUnit(bounds[1],defaultUnit)
        self.bounds = bounds

    def getValue(self):
        str = DevicePara.getValue(self)
        a=(float(str)*self.defaultUnit)
        #print(a)
        return a

    def setValue(self,val):
        val = Unit.addDefaultUnit(val,self.defaultUnit)
        self.checkBounds(val)
        str = self.makeVisaStr(val)
        self.device.write(str)

    def checkBounds(self,val):
        val = Unit.addDefaultUnit(val,self.defaultUnit)
        if val<Unit.addDefaultUnit(self.bounds[0],self.defaultUnit):
            raise ValueError("parameter %s too small"%self.visaName)
        if val>Unit.addDefaultUnit(self.bounds[1],self.defaultUnit):
            raise ValueError("parameter %s too large"%self.visaName)

    def makeVisaStr(self,val):
        return self._makeVisaStr_(val)


    def _makeVisaStr_(self,val):
        return "%s %f %s"%(self.visaName,val.asNumber(),Unit.unitStr(Unit.getUnit(val)))


class DeviceNumParaNoUnits(DeviceNumPara):
    def _makeVisaStr_(self,val):
        """first convert to default unit, then omit unit in the visa string"""
        v2 = inUnit(val,self.defaultUnit)
        return "%s %f"%(self.visaName,v2)

class DeviceNumParaCh(DeviceNumPara):
    def _makeVisaStr_(self,val):
        """first convert to default unit, then omit unit in the visa string"""
        #v2 = inUnit(val,self.defaultUnit)
        return "%s %f %s"%(self.visaName%self.device.getChannel(),val.asNumber(),Unit.unitStr(Unit.getUnit(val)))
    
    def getValue(self):
        st = self.visaName%self.device.getChannel()
        str = self.device.ask("%s?"%(st))
        return (float(str)*self.defaultUnit)

class DeviceNumParaNoUnitsCh(DeviceNumParaCh):
    """the visaString waits to be formatted with the integer corresponding to the channel"""
    def _makeVisaStr_(self,val):
        """first convert to default unit, then omit unit in the visa string"""
        v2 = inUnit(val,self.defaultUnit)
        return "%s %f"%(self.visaName%self.device.getChannel(),v2)

    



class Device(object):
    """that is the base class for every lab device"""
    def __init__(self,adr,paraClass,numParaClass):
 #       if adr == None:
 #           self.adr =  self.readDefaultAdress(self.kindOfDevice())
 #       else:
        self.adr = adr
        self.numParams = dict()
        self.paraClass = paraClass
        self.numParaClass = numParaClass

    @classmethod
    def defaultName(cls):
        return cls.__defaultName__

    def setNumValue(self,parName,val):
        par = self.numParams[parName]
        par.setValue(val)
#        self._setNumValue_(parName,val)

    def getNumValue(self,parName):
        par = self.numParams[parName]
        return par.getValue()


    def checkForBounds(self,parName,val):
        self.numParams[parName].checkBounds(val)


#    def readDefaultAdress(self,genericDevice):
#       return defaultHardware.adr[genericDevice]
        ## this will look in the dictionnary defaultHardware.adr (has to be defined in the appropriate module in the local folder of the computer) for the adress corresponding to the entry corresponding to the generic kind of device e.g. VoltGen

    def setNumParam(self,parName,*args):
        self.numParams[parName] = self.numParaClass(self,*args)

class VisaDevice(Device):
# I would have liked to do
#Device(visa.Instrument)
#but it doesn't work. Probably, visa.Instrument is an old school native class which doesn t support custom inheritence
    """that is the base class for every visa commandable device"""
    def __init__(self,adress = None,paraClass = DevicePara,numParaClass = DeviceNumPara):
        super(VisaDevice,self).__init__(adress,paraClass,numParaClass)
        self.instr = visa.instrument(self.adr)  ##this will automatically be the default adress if no arg is given


    def setString(self,name,str):
        self.write("%s %s"%(name,str))



 #   def _setNumValue_(self,name,val):
  #      par = self.numParams[name]
  #      par.setValue(val)

    def addNumPara(self,*args):
        par = DeviceNumPara(self,*args)
        self.numParams.append(par)

    def identify(self):
        print self.getIdentifyStr()

    def getIdentifyStr(self):
        return self.instr.ask("*IDN?")

    def ask(self,str):
        return self.instr.ask(str)

    def write(self,str):
        if verbose:
            print str
        return self.instr.write(str)

    def read(self):
        return self.instr.read()

class MultiChannel(object):
    def __init__(self,paraChClass = None,numParaChClass = DeviceNumParaNoUnitsCh):
        self._currentCh_ = 1
        self.paraChClass = paraChClass
        self.numParaChClass = numParaChClass

    def getChannel(self):
        return self._currentCh_
    def setChannel(self,ch):
        self._currentCh_ = ch

    def setChParam(self,parName,*args):
        """uses the parameters dedicated for one channel"""
        self.numParams[parName] = self.numParaChClass(self,*args)

class Tracer(MultiChannel,Device):
    """a Visa device that can record traces"""
    def __init__(self):
        MultiChannel.__init__(self)
        self._multiConfig_ = utils.misc.multiConfig(self.__defaultName__)
    
    def getWinName(self):
        return self.__defaultName__
    
    def quickTrace(self,name = "quickTrace",isFit = False,model = "Lorentz",win = None,**kwds):
        """get, displays saves and returns curve from current ESA, args and kwds are passed to ESA.getTrace(), for NA, there exists an argument correctForCutOff = True (by default)"""
        #na = defaultDevice("NA")
        if win is None:
            win = self.getWinName()
        s = self.getTrace(name = name,win = win,**kwds)
        if isFit:
            s.fit(model = model)
        else:
            s.plot()
#        s.setName(name = name)
        s.save()
        return s
        
    def plotTrace(self,name = "someTrace",win = None,*args,**kwds):
        """get, displays and returns curve from current ESA, args and kwds are passed to ESA.getTrace(), for NA, there exists an argument correctForCutOff = True (by default)"""
        if win is None:
            win = self.getWinName()
        t = self.getTrace(name = name,win = win,**kwds)
        t.plot()
        return t
    
    
    def recallState(self,state = -1):
        d  = self._multiConfig_.getState(state)
        self.setStateFromDict(d)
    
    def saveState(self,statename):
        d = self.saveStateToDict(statename)
        self.saveStateOnDevice(statename)
        self._multiConfig_.addState(statename,d)
    
    def saveStateToDict(self,name = ""):
        return dict()
    
    def getTrace(self,**kwds):
        """specify "model", "minSNR", "minTime" [s]
        in order to delay the acquisition by at least "minTime" or until
        a signal-to-noise of "minSNR" has been obtained"""
        try:
            AutoGenDir = kwds.pop("saveInAutoGenDir")
        except:
            AutoGenDir = True
        try:
            CSVcopy = kwds.pop("saveCSVcopy")
        except:
            CSVcopy = True
            
        tr = self._getTrace_(saveInAutoGenDir = AutoGenDir,saveCSVcopy = CSVcopy,**kwds)
        tr.toSIUnits()
        tr.measParam.update(utils.misc.getGeneralGraphVal())
        tr.measParam.update(utils.misc.getRefCellV())
        return tr

class VisaTracer(Tracer):
    def __init__(self,adress = None):
        Tracer.__init__(self)
        
        
    def _setCurrentChannelForTrace_(self):
        pass


    def _getTrace_(self,**kwds):
        fitFlag = 0
        try:
            minSNR = kwds.pop("minSNR")
            fitFlag = 1
        except KeyError:
            minSNR = 0
            fitFlag = 0
        try:
            minTime = kwds.pop("minTime")
        except KeyError:
            minTime = 0
        try:
            timeout = kwds.pop("timeout")
        except KeyError:
            timeout =30

        "initialization"
        self._initDataTransfer_()
        self._setCurrentChannelForTrace_()
        time0=time.clock()
        time.sleep(minTime)
        SNR=-1
        (mult, offset)=self._getYmathParams_()
        #print(mult,offset)
        while SNR<minSNR :
            time.sleep(1)
            Y = self._getYvalues_()
            Y = (Y-offset)*mult
            X = self._getXaxis_()#numpy.arange(Xzero,Xzero+len(Y)*Xincr-Xincr/2,Xincr)
            tr = self._getTraceObject_(X,Y,**kwds)
            #tr.toSIUnits()
            if fitFlag :
                tr.fit(plotAfterwards = True, verboseLevel = 0)
                SNR=tr.getSNR()
                print SNR
            else :
                SNR=1
            if time.clock()-time0>timeout :
                print('%ds Timeout occured'%int(timeout))
                break
#        tr.toSIUnits()
#        tr.chooseAppropriateUnits()
        return tr

    def getNaverages(self):
        return self.numParams["averages"].getValue()

    def _parseStrIntoArray_(self,tr):
        offsetByte =  int(tr[1])+2
        val = numpy.frombuffer(tr,dtype = "B",offset = offsetByte)
        return val


class Scope(VisaTracer):
    __defaultName__ = "SCOPE"
    def __init__(self,adress = ""):
        VisaTracer.__init__(self,adress = adress)
        self.numParams["t_div"] = None
        self.numParams["V_div"] = None
        self.numParams["nSamples"] = None

##########################
    #def setChannel(self,ch):
    #    self._currentCh_ = ch
    #def getChannel(self):
    #    return self._currentCh_
##########################
    def setV_div(self,V_div):
        self.setNumValue("V_div",V_div)
    def getV_div(self):
        return self.getNumValue("V_div")
##########################
    def set_t_div(self,t_div):
        self.setNumValue("t_div",t_div)
    def get_t_div(self):
        return self.getNumValue("t_div")
    def autoScale(self,keepTrace = False):
        return self._autoScale_(keepTrace = keepTrace)








class DaqmxDevice(object):
    """that is the base class for every Daqmx commandable device"""
    def __init__(self,adress = None):
        #super(DaqmxDevice,self).__init__(self,adr)
        self.task = None



class FreqGen(object):
    """Generic device able to output a sine without offset, Base class for more complex generators"""
    __defaultName__ = "FreqGen"

    def __init__(self):
        self.numParams["frequency"] = None#VisaDeviceParam("freq",1.0,Unit.kHz,[0,10])
        self.numParams["Veff"] = None#VisaDeviceParam("level",1.0,Unit.V,[0,10])
        self.numParams["Power"] = None#VisaDeviceParam("level",0.0,Unit.dBm,[-140,18])


####################
    def setVeff(self,Veff):
        """Sets the value of Veff to the specified value. the default unit for Veff is V"""
        self.setNumValue("Veff",Veff)

    def getVeff(self):
        return self.getNumValue("Veff")


#####################
    def setPower(self,Power):
        """Sets the value of the output in dBm"""
        self.setNumValue("Power",Power)

    def getPower(self):
        """Sets the value of the output in dBm"""
        return self.getNumValue("Power")
#######################

    def setFreq(self,freq): #virtual function
        self.setNumValue("frequency",freq)
    def getFreq(self): #virtual function
        return self.getNumValue("frequency")


class LFGen(FreqGen):
    """Low freq gen: the output can be different from a sine..."""
    def triangle(self,freq_hz = 10,ampl_V = 1,offset_V = 0):
        super(LFGen, self).checkForBounds(freq_hz)
        raise NotImplementedError()

    def square(self,freq_hz = 10,ampl_V = 1,offset_V = 0):
        super(LFGen, self).checkForBounds(freq_hz)
        raise NotImplementedError()


class VoltGen(Device):
    """outputs a constant voltage"""
    @classmethod
    def genericDevice(cls):
        return cls.__name__## essentialy to show the class method construction

    def setVoltage(self,V):
        raise NotImplementedError()

    def getVoltage(self):
        raise NotImplementedError()


class ArbSigGen(LFGen,VoltGen):
    """in addition to freqGeneration, can output arb waveforms"""

    def setVoltage(self,V):
        self.numParams["V"].setValue(V)
        
    def setVoltageDC(self,V_DC):
        self.numParams["V_DC"].setValue(V_DC)
        
    def setFrequency(self,f):
        self.numParams["f"].setValue(f)
        
    def setPhase(self,phi):
        self.numParams["phi"].setValue(phi)
        
    def setSine(self,V,f):
        self._setSine_()
            
    def setSquare(self,V,f):
        self._setSquare_()
        
    def setRamp(self,V,f):
        self._setRamp_()

    def setDC(self,V_DC):
        self._setDC_()
        
    def setOutput(self,d):
        self._setOutput_()
        
    def getVoltage(self):
        self._getVoltage_()
        
    def getFrequency(self):
        self._getFrequency_()
        
    def getPhase(self):
        self._getPhase_()
        
    def initPhase(self):
        self._initPhase_()
        
    def loadWaveform(self,wfm,sampleRate = 0,autorun = False):
        """loads wfm in the memory of the AWG"""
        self._loadWaveform_(wfm, sampleRate, autorun)
        
class ArbSigGenTwoChOld(LFGen,VoltGen):  
    """in addition to freqGeneration, can output arb waveforms"""
        
    def setVoltage(self,Ch,V):
        self._setVoltage_()

    def setFrequency(self,Ch,f):
        self._setFrequency_()
        
    def setPhase(self,Ch,phi):
        self._setPhase_()

    def setSine(self,Ch,V,f,phi):
        self._setSine_()
        
    def setRamp(self,Ch,V,f,phi):
        self._setRamp_()
        
    def setSquare(self,Ch,V,f,phi):
        self._setRamp_()
        
    def initPhase(self):
        self._initPhase_()
        
    def getVoltage(self,Ch):
        self._getVoltage_()
        
    def getFrequency(self,Ch):
        self._getFrequency_()
        
    def getPhase(self,Ch):
        self._getPhase_()
        
    #old version of code
    #def setVoltage(self,V,slewRate = 0):
     #   """sets the voltage as in the case of a VoltGen, in addition, user can specify maximum slope to set the voltage (0 means output directly)"""
     #   ### you will probably have to use the next function inside this one...
     #   raise NotImplementedError()



#class MultiSpannable(Spannable):
#    """Can handle different spans (segments) at once, mainly for 5061B Networkanalyzer"""
#
#    def __init__(self):
#        self.SpanArray=[]
#
#
#
#        self.SpanArray.append(obj)


class Spannable(object):
    def __init__(self):
        self.numParams["start"] = None
        self.numParams["stop"] = None
        self.numParams["span"] = None
        self.numParams["center"] = None


    def getSpan(self):
        return self.getNumValue("span")

    def getStart(self):
        return self.getNumValue("start")
    
    def getStop(self):
        return self.getNumValue("stop")
    
    def getCenter(self):
        return self.getNumValue("center")

    def getSweepTime(self):
        return self.getNumValue("sweeptime")
    
  #  def getAverages(self):
  #      return self.getNumValue("averages")
    
    def setStart(self,start):
        self.setNumValue("start",start)

    def setStop(self,stop):
        self.setNumValue("stop",stop)

    def setSpan(self,span):
        self.setNumValue("span",span)

    def setCenter(self,center):
        self.setNumValue("center",center)

    def setRange(self,ran):
        if ran[0]<ran[1]:
            self.setStart(ran[0])
            self.setStop(ran[1])
        else:
            self.setStart(ran[1])
            self.setStop(ran[0])

    def setAverages(self,averages):
        self.setNumValue("averages",averages)

    def setPoints(self,points):
        self.setNumValue("points",points)

    def setSweepTime(self,sweeptime):
        self.setNumValue("sweeptime",sweeptime)
    
#    def getSweepTime(self):
#        return self.getNumValue("sweeptime")

    def setAutoSweepTime(self):
        self._setAutoSweepTime_()

    def restart(self):
        self._restart_()

class ESA(Spannable,VisaTracer,MultiChannel):
    #__defaultName__ = "ESA"
    def __init__(self):
        Spannable.__init__(self)
        VisaTracer.__init__(self)
        #MultiChannel.__init__(self)
        self.__minimumSNR__=-1.0

    def _getTraceObject_(self,X,Y,**kwds):
        """asssumes X is in Hertz and Y in dBm"""
        if self.getSpan().asNumber()==0:
            unitX = s
        else:
            unitX = Unit.Hz
        return Spectrum.traceDBM_per_Hz(X,Y,self.getRBW(),unit_x = unitX,**kwds)


    def _getTrace_(self,**kwds):
        tr = VisaTracer._getTrace_(self,**kwds)
        tr.measParam["rbw"] = self.getRBW()
        tr.measParam["start"] = self.getStart()
        tr.measParam["stop"] = self.getStop()
        tr.measParam["center"] = self.getStart()
        return tr
    def setRBW(self,RBW):
        self.setNumValue("RBW",RBW)
    def getRBW(self):
        return self.getNumValue("RBW")
    def setRBWAuto(self):
        self._setRBWAuto_()
    def restart(self):
        self._restart_()
        
    def getNPoints(self):
        return self._getNPoints_()


class NetworkAnalyzer(FreqGen,Spannable,VisaTracer,MultiChannel):
    __defaultName__ = "NA"
    
    
    
    def __init__(self,adr = ""):
        FreqGen.__init__(self)
        Spannable.__init__(self)
        MultiChannel.__init__(self)
        VisaTracer.__init__(self)


    @classmethod
    def correctForCutOff(cls,trace,coeffs = [(1/1.15732e8)**8,0,0,0,(1/8.78479e7)**4,0,(1/1.1828e8)**2,0,1]):
        """multiplies by the corresponding polynomial"""
        mult = numpy.polyval(coeffs,trace.X)
        Y = trace.Y*mult
        trace.setXY(trace.X,Y)
        trace.measParam["correctForCutOff"] = True
        for i,c in enumerate(coeffs):
            trace.measParam["CutOffCoeff%i"%i] = c
        trace.name = trace.name + "_cor"
        
    def _getTraceObject_(self,X,Y,**kwds):
        """asssumes X is in Hertz and Y in dB"""
        if self.getSpan().asNumber()==0:
            unitX = s
        else:
            unitX = Hz
        if self.getFormat() == "MLOG":
            return Spectrum.traceDB(X,Y,unit_x = unitX,**kwds)
        if self.getFormat() == "MLIN":
            return Spectrum.traceLin(X,Y,unit_x = unitX,**kwds)
        if self.getFormat() == "PHAS":
            return Spectrum.traceLin(X,Y,unit_x = unitX,**kwds)

        


    def setRBW(self,RBW):
        self.setNumValue("RBW",RBW)
    def getRBW(self):
        return self.getNumValue("RBW")
    def setRBWAuto(self):
        self._setRBWAuto_()
    def restart(self):
        self._restart_()

    def _getTrace_(self,correctForCutOff = True,**kwds):
        tr = VisaTracer._getTrace_(self,**kwds)
        tr.measParam["rbw"] = self.getRBW()
        tr.measParam["start"] = self.getStart()
        tr.measParam["stop"] = self.getStop()
        tr.measParam["center"] = self.getStart()
        tr.measParam["power"] = self.getPower()
        tr.measParam["Naverages"] = self.getNaverages()
        if correctForCutOff:
            if isinstance(tr,Spectrum.traceDB):
                self.correctForCutOff(tr)
        return tr
    
    
class AOBoard(ArbSigGen,DaqmxDevice):
    adr = "mod2ao..."
    def __init__(self):
        DaqmxDevice.__init__(self,self.adr)

    @classmethod
    def genericDevice(cls):
        return cls.__name__## essentialy to show the class method construction

    ### here, you only need to implement the loadWaveform function, the rest will automatically work due to functions of parent classes

class LaserDiode(Device,Spannable):
    def __init__(self):
        #Device.__init__(self)
        Spannable.__init__(self)# VisaDevice.__init__(self,adress)

    def setLambda(self,lambda_value):
        self.numParams["lambda_value"].setValue(lambda_value)

    def getLambda(self):
        self._getLambda_()

    def setCurrent(self,current):
        self.numParams["current"].setValue(current)

    def getCurrent(self):
        self._getCurrent_()

    def setForwardSlewRate(self,forward_slew_rate):
        self.numParams["forward_slew_rate"].setValue(forward_slew_rate)

    def getForwardSlewRate(self):
        self._getForwardSlewRate_()

    def isTheScanOver(self):
        return False


    def startScan(self,userStop = False,loop = False): # scan with possibility to stop at one point
        loopIt = True
        while(loopIt):
            self._startScan_()
            if userStop:
                while self.ask("*opc?") == "0":
                    raw_input("press enter to stop scan")
                    self.stopScan()
                    isQ = raw_input("press enter to restart scan (q to quit scan)")
                    if isQ == "q":
                        return
                    self.reStartScan()
                    time.sleep(0.1) # time delay so that laser will reach 'end of scan' right at the end, so that *opc will give 1 to exit the program
            loopIt = loop
            if loop:
                self.resetScan()
    def reStartScan(self):
        self._reStartScan_()
                
    def stopScan(self):
        self._stopScan_()

    def setStart(self,lambda_start):
        self.numParams["lambda_start"].setValue(lambda_start)

    def setStop(self,lambda_stop):
        self.numParams["lambda_stop"].setValue(lambda_stop)

    def resetScan(self):
        self._resetScan_()

    def _getLambda_(self):
        print self.ask(":wave?")

    def _getCurrent_(self):
        print self.ask(":sense:curr:diod")

    def _getForwardSlewRate_(self):
        print self.ask(":wave:slew:forw?")

    def _resetScan_(self):
        self.write(":output:scan:reset")

    def _startScan_(self):
        self.resetScan()
        while self.ask("*opc?") == "0":
            pass
        self.write(":output:scan:start")

    def _reStartScan_(self): # function used to restart a scan after stopping (no reset scan)
        self.write(":output:scan:start")

    def _stopScan_(self):
        self.write(":output:scan:stop")

from hardwareDevices import *

print "devices imported"
