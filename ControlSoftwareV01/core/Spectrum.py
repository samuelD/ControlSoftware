
import pylab
import os
import csv
import math
import numpy
import loadSave
import utils
import ConfigParser
from utils import readConfig
#from ..hardware import hardwareDevices
import fit
from utils import Unit
#from fit import LORENTZ,GAUSS,LORENTZ_GAUSS
import plotting
#import ToroidAll
#import tkFileDialog
#import cfg3He
from scipy import signal
#import hardware
#try :
#    import hardware
#except ImportError:
#    pass

from plotting import Plottable,Fittable
#######################################################################
### Do never ever change these definitions                          ###
### Changing or removing a field will lead to compatibility problems###
#######################################################################
#__MEAS_PARAM__ = "MEAS_PARAM"
__VID_BW__  = "video_BW"
__RBW__     = "RBW"

__DATA__  = "DATA"
#__TRACE__ = "trace"

__X_HZ__ = "X (Hz)"
__Y_V__  = "Y (V)" 		
########################################################################
########################################################################
########################################################################
class __Trace__:
    """the class containing data from instruments
    has to be initialyzed with a table of rawData (to be saved in the CSV file)"""
    def __init__(self,rawX,rawY):
        #if(Ylog!=[]):
        #    Y1 = utils.dBmToVolts(Ylog)
        #    self.Ylog = Ylog
        #    Fittable.__init__(self,Y = Y1,**kwds)
        #    print "from Ylog"
        #else:
        #    Fittable.__init__(self,**kwds)
        self.rawX = rawX
        self.rawY = rawY
        
        
    def __load__(self,f,cp):
        Fittable.__load__(self,f,cp)
    

    def saveCSV(self,filename): 
        """saves the data found in self.rawX and self.rawY in a CSV file"""
        ##this function overwrights the function of Plottable object because we wanna save the Ylog instead of linear values
        #data = numpy.array([self.X,Unit.Veff_sq2dBm_array(self.Y)])
        data = numpy.array([self.rawX,self.rawY])
        numpy.savetxt(filename,data.transpose(),delimiter = ",",fmt = "%.9g")
            

#class speOld(__Trace__):
#    """class for Spectrum loaded from a csv file...
#    in this case, crucial information like the RBW is not saved with the data, which prevents
#    some routines from being excuted on these objects"""
#    __EXT__="csv"
#
#    def __init__(self,**kwds):
#        __Trace__.__init__(self)


class traceDBM(__Trace__,Fittable):
    """Object that contains at the same time rawX rawY from the ESA and X, Y in SI units""" 
    
    def __init__(self,rawX,rawY,**kwds):
#        loadSave.Saveable.__init__(self,**kwds)
        __Trace__.__init__(self,rawX,rawY)
        Fittable.__init__(self,X = rawX,Y = Unit.dBm2W(rawY),unit_y = Unit.W,**kwds)

class traceDBM_per_Hz(__Trace__,Fittable):
    def __init__(self,rawX,rawY,rbw,**kwds):
#        loadSave.Saveable.__init__(self,**kwds)
        __Trace__.__init__(self,rawX,rawY)
        try:
            self.measParam["rbw"] = rbw
        except (AttributeError,RuntimeError):
            self.measParam = {"rbw" : rbw}
        rbw = Unit.toSI(rbw).asNumber()
        Fittable.__init__(self,X = rawX,Y = Unit.dBm2W(rawY)/rbw,unit_y = Unit.W/Unit.Hz,**kwds)


class traceDB(__Trace__,Fittable):
    """typically from NA amp"""
    def __init__(self,rawX,rawY,**kwds):
#        loadSave.Saveable.__init__(self,**kwds)
        __Trace__.__init__(self,rawX,rawY)
        Fittable.__init__(self,X = rawX,Y = Unit.dB2Number(rawY),unit_y = None,**kwds)

class traceLin(__Trace__,Fittable):
    """Object that contains at the same time rawX rawY from the ESA and X, Y in SI units""" 
    
    def __init__(self,rawX,rawY,**kwds):
#        loadSave.Saveable.__init__(self,**kwds)
        __Trace__.__init__(self,rawX,rawY)
        Fittable.__init__(self,X = rawX,Y = rawY,**kwds)


class speOpt(Plottable):
    """the class for optical spectrum : """
    __EXT__ = "spo"
    def __init__(self,**kwds):
  #      loadSave.Saveable.__init__(self,**kwds)
        Plottable.__init__(self)
        # hardware.readOpticalTrace(self)
        
    def __load__(self,f,cp):
        Plottable.__load__(self,f,cp)
 
    def filter(self):
        (b,a) = signal.butter(4,0.0001,btype = "high")
        self.Yfiltered = signal.lfilter(b,a,self.Y)
        pylab.figure()
        pylab.plot(self.X,self.Yfiltered)
        self.noise =  math.sqrt(self.Yfiltered.var())
        self.threshold = - 5 * self.noise
        pylab.plot([self.X[0],self.X[-1]],[self.threshold,self.threshold])
        indexStop = -1
        indexStart = 0
        inInt = False
        self.peaks = []
        self.aboveThreshold = [i for i,j in enumerate(self.Yfiltered) if j<self.threshold]
        
        self.startInt = [self.aboveThreshold[0]]
        self.startInt.extend([j for i,j in enumerate(self.aboveThreshold[1:]) if self.aboveThreshold[i]< j-1000])
        self.stopInt = [j for i,j in enumerate(self.aboveThreshold[:-1]) if self.aboveThreshold[i+1]> j+1000]
        self.stopInt.append(self.aboveThreshold[-1])
        
        
        for i,j in zip(self.startInt,self.stopInt):
            start = i-2000
            stop = i+2000
            peak = opticalLine(self.X[start:stop],-self.Y[start:stop])
            peak.fit()
            self.peaks.append(peak)
    

    def findPDHres(self):
        self.noisePDH =  math.sqrt(self.Y.var())
        self.thresholdPDH = 5*self.noisePDH
        self.peaks = []
        indexStop = -1
        indexStart = 0
        inInt = False
        self.peaks = []  
        self.aboveThreshold = [i for i,j in enumerate(self.Y) if abs(j)>self.thresholdPDH]
        
        self.startInt = [self.aboveThreshold[0]]
        self.startInt.extend([j for i,j in enumerate(self.aboveThreshold[1:]) if self.aboveThreshold[i]< j-1000])
        self.stopInt = [j for i,j in enumerate(self.aboveThreshold[:-1]) if self.aboveThreshold[i+1]> j+1000]
        self.stopInt.append(self.aboveThreshold[-1])
        
        
        for i,j in zip(self.startInt,self.stopInt):
            start = max(i-2000,0)
            stop = min(i+2000,len(self.X))
            print start
            print stop
            peak = opticalLine(self.X[start:stop],-self.Y[start:stop])
            peak.fit()
            self.peaks.append(peak)

#    def nextRes(self,i):
#        hardware.laserPiezzoScan(wavelength = self.peaks[i].nu,ampl = 3)


    

#    def plot(self):
#        peaks = self.peaks
#        if plotting.optWin.isVisible()==False:
 #           plotting.optWin.show()
 #       self.plotInCanvas(plotting.optWin.mpl_high.canvas)            
# 
#        for j,i in enumerate(self.peaks):
#            an = plotting.optWin.mpl_high.canvas.ax.annotate("%i"%j,xy = (i.nu,0.0),xytext = (i.nu,0.015),arrowprops=dict(arrowstyle="->"))
#            an.set_picker(True)
            
#        plotting.optWin.mpl_high.canvas.draw()
#        plotting.optWin.mpl_high.canvas.mpl_connect('pick_event', self.on_pick)

        
    def on_pick(self,event):
        self.set_current_peak(int(event.artist.get_text()))
        
        
#    def set_current_peak(self,nr):
#        self.currentPeak = nr
#        self.peaks[nr].plot(canvas = plotting.optWin.mpl_low.canvas)               
    

class opticalLine(__Trace__):
    def __init__(self,X_nm,Y):
        self.nu = X_nm[0]
        __Trace__.__init__(self,utils.misc.nmToMHz(X_nm),Y,fitModel="Lorentz")

#    def plot(self,**args):
#        __Trace__.plot(self,canvas = plotting.optWin.mpl_low.canvas)
#        pylab.xlabel("detuning laser (MHz)")
#        pylab.title("peak @ %3.1f nm"%self.nu)



#loadSave.Saveable.ext[speOpt.__EXT__] = speOpt
#loadSave.Saveable.ext[speNew.__EXT__] = speNew
#loadSave.Saveable.ext[speOld.__EXT__] = speOld





#def getSpe(name = "newSpectrum",traceNr = 1,**kwds):
#    n = name
#    try:
#        kwds["path"]
#    except KeyError:
#        autoGenDir = True
#    sp = speNew(name = n,saveInAutoGenDir = autoGenDir,**kwds)
#   tn = traceNr
#   hardware.readTrace(sp,traceNr = tn)
#    sp.saveCSVcopy = True
    
   
#    return sp

#def getOpt(**kwds):
#    try:
#        kwds["path"]
#    except KeyError:
#        autoGenDir = True
#
#    spo = speOpt(saveInAutoGenDir = autoGenDir,**kwds)
#    hardware.readOpticalTrace(spo)
#    spo.saveCSVcopy = True


#    if (spo.path == ""):
#        spo.setPathToNextTrace()
#    return spo






#def lookForOptResOnPDH(**kwds):
#    """PDH signal should be plugged on ch2 of scope
#    wavelength out of laser should be plugged to channel 3
#    """
#   spo = getOpt(**kwds)
#   #hardware.readOpt(spo)
#    #spo.saveCSVcopy = True
#    #if (sp.path == ""):
#    #    sp.setPathToNextTrace()
#    spo.findPDHres()
#    spo.nextRes(0)
#    return spo

#def quickSpe(name = "quickSpectrum",model = LORENTZ,traceNr = 1,**kwds):
#    """this function calls successively the 3 functions
#getSpe()->fit()->save()->plot()"""
#    fm = model
#    n = name
#    tn = traceNr
#    esa = hardwareDevices.defaultDevice("ESA")
#    sp = esa.getTrace(name = name,**kwds)#n,model = fm,traceNr = tn,**kwds)
#    sp.fit(model = fm)
#    sp.save()
#    sp.plot()
#    return sp


#print "Spectrum imported"




class container:
    def __iter__(self):
        return testIter()


class testIter:
    def __init__(self):
        self.i = 0
    def __iter__(self):
        return self
    def next(self):
        self.i = self.i + 1
        if self.i>3:
            raise StopIteration()
        return self
