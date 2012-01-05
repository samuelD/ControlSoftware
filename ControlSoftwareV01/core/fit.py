import ConfigParser
import math
import scipy
from scipy import optimize
import numpy
from numpy import inf
import sys
import pylab
import flags
import sys
import utils
sys.path.append(utils.path.getUserDir())
import TLS
import SampleConstants
import dataAnalysis
import formulaNA
#import dataAnalysis
#import TLS
#import constants
from PyQt4 import QtCore
from numpy import isscalar,asarray 
import plotting
#import matplotlib.pyplot as plt

#from IPython.Debugger import Tracer; debug_here = Tracer()


#######################################################################
### Do never ever change these definitions                          ###
### Changing or removing a field will lead to compatibility problems###
#######################################################################
__FIT_TYPE__   = "FIT_TYPE"
__TYPE__       = "type"
LORENTZ        = "Lorentz"
GAUSS          = "Gauss"
LORENTZ_GAUSS  = "LorentzGauss"
LINEAR         = "Linear"

__FIT_PARAMETERS__ = "FIT_PARAMETERS"
__GAMMA_HZ__       = "gamma_hz"
__GAMMA_2_HZ__     = "gamma_2_hz"

__X0_HZ__          = "x0_hz"
__X0_2__           = "x0_2_hz"

__SLOPE__          = "slope"
__AMPL__           = "amplitude"

__AREA__           = "area"
__AREA_2__         = "area_2"

__OFFSET__         = "offset"
__PHI__            = "phi"

__SLOPE__          = "slope"
########################################################################
########################################################################
########################################################################
#from . import plotting
from plotting import Plottable
fitter = dict()


##### the next 3 functions are a copy paste from scipy\optimize\minpack.py (slightly modified to not throw unwanted exceptions)
def _general_function(params, xdata, ydata, function):
    return function(xdata, *params) - ydata

def _weighted_general_function(params, xdata, ydata, function, weights):
    return weights * (function(xdata, *params) - ydata)

def curve_fit(f, xdata, ydata, p0=None, sigma=None, **kw):
    """
    Use non-linear least squares to fit a function, f, to data.

    Assumes ``ydata = f(xdata, *params) + eps``

    Parameters
    ----------
    f : callable
        The model function, f(x, ...).  It must take the independent
        variable as the first argument and the parameters to fit as
        separate remaining arguments.
    xdata : An N-length sequence or an (k,N)-shaped array
        for functions with k predictors.
        The independent variable where the data is measured.
    ydata : N-length sequence
        The dependent data --- nominally f(xdata, ...)
    p0 : None, scalar, or M-length sequence
        Initial guess for the parameters.  If None, then the initial
        values will all be 1 (if the number of parameters for the function
        can be determined using introspection, otherwise a ValueError
        is raised).
    sigma : None or N-length sequence
        If not None, it represents the standard-deviation of ydata.
        This vector, if given, will be used as weights in the
        least-squares problem.


    Returns
    -------
    popt : array
        Optimal values for the parameters so that the sum of the squared error
        of ``f(xdata, *popt) - ydata`` is minimized
    pcov : 2d array
        The estimated covariance of popt.  The diagonals provide the variance
        of the parameter estimate.

    Notes
    -----
    The algorithm uses the Levenburg-Marquardt algorithm:
    scipy.optimize.leastsq. Additional keyword arguments are passed directly
    to that algorithm.

    Examples
    --------
    >>> import numpy as np
    >>> from scipy.optimize import curve_fit
    >>> def func(x, a, b, c):
    ...     return a*np.exp(-b*x) + c

    >>> x = np.linspace(0,4,50)
    >>> y = func(x, 2.5, 1.3, 0.5)
    >>> yn = y + 0.2*np.random.normal(size=len(x))

    >>> popt, pcov = curve_fit(func, x, yn)

    """
    if p0 is None or isscalar(p0):
        # determine number of parameters by inspecting the function
        import inspect
        args, varargs, varkw, defaults = inspect.getargspec(f)
        if len(args) < 2:
            msg = "Unable to determine number of fit parameters."
            raise ValueError(msg)
        if p0 is None:
            p0 = 1.0
        p0 = [p0]*(len(args)-1)

    args = (xdata, ydata, f)
    if sigma is None:
        func = _general_function
    else:
        func = _weighted_general_function
        args += (1.0/asarray(sigma),)
    res = optimize.leastsq(func, p0, args=args, full_output=1, **kw)
    (popt, pcov, infodict, errmsg, ier) = res
    
    print errmsg
    if ier not in [1,2,3,4]:
        msg = "Optimal parameters not found: " + errmsg
        print errmsg
        #raise RuntimeError(msg)

    if (len(ydata) > len(p0)) and pcov is not None:
        s_sq = (func(popt, *args)**2).sum()/(len(ydata)-len(p0))
        pcov = pcov * s_sq
    else:
        pcov = inf

    return popt, pcov




def registerFit(cls):
    global fitter
    fitter[cls.ID_STR] = cls
    return cls

def createPanelParams():
    global fitter
    for k,v in fitter.iteritems():
        v.createPanelParams()

class Fitter(Plottable):
    """parent class for fits"""
    
    panelParams = None
    
    @classmethod
    def registerClass(cls):
        fitter[cls.ID_STR] = cls

    @classmethod
    def popoutParams(cls,dictKwds):
        d = dict()
        for paraName in cls.PARAMS:
            try:
                d[paraName]=dictKwds.pop(paraName)
            except KeyError:
                pass
        return d

    def resetData(self):
        self.Xdata = self.parentCurve.X
        self.Ydata = self.parentCurve.Y
        self.X = self.parentCurve.X
        
    def excludeXRegion(self,X1,X2):
        X = []
        Y = []
        for x,y in zip(self.Xdata,self.Ydata):
            if x<X1 or x>X2:
                X.append(x)
                Y.append(y)
        self.Xdata = numpy.array(X)
        self.X = numpy.array(X)
        self.Ydata = numpy.array(Y)


    def setParent(self,parent):
        self.Xdata = parent.Xdata  ### don't worry, arrays are passed by address...
        self.Ydata = parent.Ydata

    def currentGuess(self,parName):
        """returns the current guess value for parName"""
        return self.param_guess[parName]

    def isFixed(self,parName):
        return parName in self.param_fixed
    #self.panelParams.isFixed(parName)
     
    def isGuess(self,parName):
        if not self.isUsePanel():
            return self.is_guess_required()
        return self.panelParams.isGuess(parName)
        
    def getXrangeLine(self):
        [minFit,maxFit] = Plottable.getXrangeLine(self.parentCurve)
        [minPar,maxPar] = Plottable.getXrangeLine(self.parentCurve)
        return [min(minFit,minPar),max(maxFit,maxPar)]
    def getYrangeLine(self):
        [minFit,maxFit] = Plottable.getYrangeLine(self.parentCurve)
        [minPar,maxPar] = Plottable.getYrangeLine(self.parentCurve)
        return [min(minFit,minPar),max(maxFit,maxPar)]



    @classmethod
    def createPanelParams(cls):
        from ..GUI import Qt_FitterParams
        cls.panelParams = Qt_FitterParams.Qt_FitterParams(cls)

    def __init__(self,parameters = None,name="fit",parentCurve = None,usePanelParams = None,**kwds):
        pc = parentCurve
        n = name
        self.iterNr = 0
        
        
        if parentCurve == None:
            Xdata = []
            Ydata = []
            isScaleOnMe = True
        else:
            Xdata = numpy.array(parentCurve.X)
            Ydata = numpy.array(parentCurve.Y)
            isScaleOnMe = parentCurve.scaleOnMe
        super(Fitter,self).__init__(X=Xdata,Y=numpy.zeros(len(Xdata)),parentCurve = pc,name = n,scaleOnMe = isScaleOnMe)
        self.Xdata = Xdata  ### don't worry, arrays are passed by address...
        self.Ydata = Ydata
        self.param_guess = dict()

        self.guessCurve = None
        
        self.param_fitted = dict()
        self.fitDone = True
        self.verboseLevel = 1
        if parameters!=None:
            for paraName in self.PARAMS:
                try:
                    self.param_fitted[paraName] = parameters[paraName]
                except KeyError:
                    self.fitDone = False
                    print "Value not found for parameter %s of fitter %s"%(paraName,self.name)
        else:
            self.fitDone = False
        if self.fitDone:
            self.X = self.Xdata
            self.Y = self.func(self.Xdata,self.packParams())
            
        if flags.GUIon:   
            self.connectToPanelParams()
            if usePanelParams == None:
                self._usePanel_ = self.panelParams.isVisible()
            else:
                self._usePanel_ = usePanelParams
            if usePanelParams:
                self.showPanelParams()
            
        
        
    def __fit_with_this__(self,X,*par):    
        par2 = []
        for i in par:
            par2.append(i)
        par2.reverse()
        newPar = []
        for i in self.PARAMS:
            if i in self.param_fixed:
                newPar.append(self.param_fixed[i])
            else:
                newPar.append(par2.pop())
        #print "par" + str(par)
        #print "newPar " + str(newPar)            
        return self.func(X,newPar)

    def __minimizeMe__(self,par):
        """a customized function that uses the self.fixed_param values"""
        try:
            par2 = par.tolist()
        except AttributeError:
            par2 = par
        par2.reverse()
        newPar = []
        for i in self.PARAMS:
            if i in self.param_fixed:
                newPar.append(self.param_fixed[i])
            else:
                newPar.append(par2.pop())
        #print "par" + str(par)
        #print "newPar " + str(newPar)            
        return self.__minimizeMeFree__(newPar)

    def __minimizeMeFree__(self,par):
        """this function is the function to be minimized (outputs the vector of residuals) in the case of all parameters are free"""
        if self.verboseLevel>1:
            self.iterNr = self.iterNr +1
            print "iterationNr : %s"%self.iterNr
        f = self.func
        return f(par)-self.Ydata

 #   def __minimizeMeFixed__(self,par):
 #       """this function is the function to be minimized (outputs the vector of residuals) in the case where some parameters are fixed"""
 #       for i in self.fixParNr:
 #           par[i] = self.fixParVal[i]
 #       return self.__minimizeMeFree__(par)#


    def plot(self,plotNicely = False,nicePlotNpoints = 5e4,**kwds):
       # print "plotting fitter"
        if self.fitDone:
            if(plotNicely):
                back = self.Xdata
                min = self.Xdata.min()
                max = self.Xdata.max()
                span = max-min
                self.Xdata = numpy.arange(min,max,span/nicePlotNpoints)
                self.getYvalues(self.packParams())

            Plottable.plot(self,**kwds)
            if(plotNicely):
                self.Xdata = back
                self.getYvalues(self.packParams())
#           p.set_label(self.makeLabel())

    


    def plotGuess(self,*args,**kwds):
        self.getGuessParamsFromGui()
        if self.guessCurve is not None:
            self.guessCurve.setXY(X = self.X, Y = self.func(self.X,self.packParamsGuess()))
        else:
            self.guessCurve = plotting.plot(self.X, self.func(self.X,self.packParamsGuess()) ,parentCurve = self.parentCurve,name = "guess for fit",linestyle = "--",color = "red")
        self.guessCurve.plot()
       
    
    def fitOnly(self):
        """only performs the fit, using the self.param_guess as guess and self.param_fixed as fixed params"""
        try:
            res = curve_fit(self.__fit_with_this__,self.Xdata,self.Ydata,self.packParamsGuess())
            self.unpackParam(res[0])
            self.fitFlag = res[1]
        except RuntimeError as e:
            if self.isUsePanel():
                self.emit(QtCore.SIGNAL("fitFailled"))
            if self.verboseLevel>0:
                print e
            return False
    
        return True

    def getResiduals(self):
        if self.fitDone is False:
            return None
        return self.func(self.X,self.packParams())-self.Ydata

    def getYvalues(self,par):
        (self.X,self.Y) = (self.Xdata,self.func(self.Xdata,par))

  #  def interactiveGuess(self,**kwds):
  #      raise NotImplementedError("no interactive Guess parameter function implemented for that kind of fit")

    def guessParamsFromCursors(self,x1,y1,x2,y2):
        print "no guessParamsFromCursors implemented for %s, will use the default guess algorythm"%self.__class__.__name__
        self.guessParam()


    def setToGuessParams(self,gp):
        """update the self.param_to_guess with these new ones, 
        in addition, send these values to the GUI if panelParams exists 
        (also changes the property to guess_this)"""
        if gp == None:
            return
        self.param_to_guess.update(gp)
        if gp is not None:
            if self.isUsePanel():
                self.emit(QtCore.SIGNAL("paramToGuessChanged"),self.param_to_guess)

    def setFreeParams(self,gp):
        """update the self.param_free with these new ones, 
        in addition, send these values to the GUI if panelParams exists 
        (also changes the property to free)"""
        if gp == None:
            return
        self.param_free.update(gp)
        if gp is not None:
            if self.isUsePanel():
                self.emit(QtCore.SIGNAL("paramFreeChanged"),self.param_free)
        
    def setFixedParams(self,fp):
        if fp == None:
            return
        self.param_fixed.update(fp)
        if fp is not None:
            if self.isUsePanel():
                self.emit(QtCore.SIGNAL("paramFixChanged"),self.param_fixed)

    def isUsePanel(self):
        if self._usePanel_ == None:
            return self.panelParams.isVisible()
        return self._usePanel_

    def getFreeParams(self):
        #self.param_free = dict()
        if self.isUsePanel():
            self.param_free = self.panelParams.getFreeParams()
    
    
    def getFixedParams(self):
        #self.param_fixed = dict()
        if self.isUsePanel():
            self.param_fixed = self.panelParams.getFixedParams()
    
    def getToGuessParams(self):
        #self.param_to_guess = dict()
        if self.isUsePanel():
            self.param_to_guess = self.panelParams.getToGuessParams()
                
    def getGuessParamsFromGui(self):
        """returns all guess params, irrespective of what type of constraints they have"""                
        if self.isUsePanel():
            self.param_guess = self.panelParams.getGuessParams()
        
        
    def is_guess_required(self):
        if self.param_to_guess is None:
            return False
        return len(self.param_to_guess)>0
        
    def resetFreeRemoveFixed(self):
        """Puts back the parameters (that might have been changed by the autoguess function)
         to the values they should have, and remove fixed params from the guess"""    
        for i in self.param_fixed:
            if i in self.param_guess:
                self.param_guess.pop(i)
        self.param_guess.update(self.param_free)
                
    def fillMissingParamsInToGuess(self):
        """all params which are not in param_fixed or param_free are added with value 0 in param_to_guess"""
        for i in self.PARAMS:
            if i not in self.param_to_guess:
                if i not in self.param_fixed:
                    if i not in self.param_free:
                        self.param_to_guess[i] = 0.0
       
       
    def getParamAnyVal(self,par):
        try:
            return self.param_fixed[par]
        except KeyError:
            pass
        try:
            return self.param_to_guess[par]
        except KeyError:
            pass
        try:
            return self.param_free[par]
        except KeyError:
            pass
       
    def doGuess(self,param_fixed = None,param_free = None,param_to_guess = None):
        """first, assign the parameters that are passed as optional args,
        then guess parameters and then reset the one that are fixed to what they should..."""
        
        self.param_fixed = dict()
        self.param_free = dict()
        self.param_to_guess = dict()
        
        self.setFixedParams(param_fixed)
        self.setFreeParams(param_free)
        self.setToGuessParams(param_to_guess)
        
        self.getFixedParams()
        self.getFreeParams()
        self.getToGuessParams()
        self.fillMissingParamsInToGuess()
        
        self.param_guess.update(self.param_free)
        self.param_guess.update(self.param_to_guess)
        
        if self.is_guess_required():
            self.param_guess.update(self.guessParam())
        self.resetFreeRemoveFixed()
        if self.isUsePanel():
            self.emit(QtCore.SIGNAL("paramGuessDetermined"),self.param_guess) 
                
    def fit(self,cursorVal = None,param_fixed = None,param_free = None,param_to_guess = None,verboseLevel = 1):
        """performs a fit, param_fixed is a dictionnary containing {param_name:value}
        param_free contains parameters who are free but guess_value cannot be twickled around
        param_to_guess is a dictionnary containing parameter value pairs for the parameters for which
        guess_value can be twickled (in fact, all missing parameters will enter this category...)
        """
        #print "a fit should be performed by" + str(self)
        self.verboseLevel = verboseLevel
        #self.param_guess = paramGuess
        
        self.doGuess(param_fixed,param_free,param_to_guess)
        
        if self.isUsePanel():
            self.emit(QtCore.SIGNAL("setMeAsCurrent"),self)
        
        #self.doGuess()
        #if interactiveGuessParams!=None:
        #    self.interactiveGuess(**interactiveGuessParams)
        if cursorVal != None:
            x1 = cursorVal[0]
            y1 = cursorVal[1]
            x2 = cursorVal[2]
            y2 = cursorVal[3]
            self.guessParamsFromCursors(x1,y1,x2,y2)
        
        if not self.fitOnly():
            if self.isUsePanel():
                while self.panelParams.isStopped():
                    flags.app.processEvents()
            return
        self.getYvalues(self.packParams())

        if self.verboseLevel>0:
            self.outputPar()


        self.fitDone = True
        if self.isUsePanel():
            self.emit(QtCore.SIGNAL("fitDone"),self.param_fitted)
        self.waitForOK()
    

    def waitForOK(self):
        if not self.isUsePanel():
            return
        self.panelParams.waitForOK()

    def saveFp(self,fp):
        c = ConfigParser.ConfigParser()

        ###save the type of fit:
        c.add_section(__FIT_TYPE__)
        c.set(__FIT_TYPE__,__TYPE__,self.ID_STR)


        ###save the fit parameters
        c.add_section(__FIT_PARAMETERS__)
        for p in self.param_fitted:
            c.set(__FIT_PARAMETERS__,p,self.param_fitted[p])
        c.write(fp)
        #with open(savefile + ".fit","w") as f:



    def packParams(self):
        par = []
        for paraName in self.PARAMS:
            par.append(self.param_fitted[paraName])
        return par


    def packParamsGuess(self):
        """without adding other parameters in"""
        par = []
        for paraName in self.PARAMS:
            if paraName in self.param_guess:
                par.append(float(self.param_guess[paraName]))
            #else:
            #    par.append(float(self.param_fixed[paraName]))
        return par


    def unpackParam(self,par):
        """also takes care of parameters that are fixed"""
        self.param_fitted = dict()
        try:
            par = par.tolist()
        except AttributeError:
            pass
        par.reverse()
        for i,paraName in enumerate(self.PARAMS):
            if paraName in self.param_guess:
                self.param_fitted[paraName] = par.pop()
            else:
                self.param_fitted[paraName] = self.param_fixed[paraName]

    def outputPar(self):
        self.saveFp(sys.stdout)

  #  def showAndConnectPanelParams(self):
   #     self.emit(QtCore.SIGNAL("showPanelParams"))

   # def _showAndConnectPanelParams_(self):
    #    """this function should'nt be executed only by main thread"""
    #    if self.panelParams is not None:
     #       return
      #  else:
       #     print "before showPanel"
        #    self.showPanelParams()
         #   print "after showPanel"
          #  self.connectToPanelParams()
           # print "after connectPanel"


    def displayMeInPanel(self):
        self.emit(QtCore.SIGNAL("setMeAsCurrent"),self)
        self.emit(QtCore.SIGNAL("showPanelParams"))


    def connectToPanelParams(self):
        self.connect(self,QtCore.SIGNAL("setMeAsCurrent"),self.panelParams.setFitterAsCurrent)
        self.connect(self,QtCore.SIGNAL("fitDone"),self.panelParams.updateFittedValues)
        self.connect(self,QtCore.SIGNAL("paramToGuessChanged"),self.panelParams.paramToGuessChanged)
        self.connect(self,QtCore.SIGNAL("paramFreeChanged"),self.panelParams.paramFreeChanged)
        self.connect(self,QtCore.SIGNAL("paramFixChanged"),self.panelParams.paramFixedChanged)
        self.connect(self,QtCore.SIGNAL("paramGuessDetermined"),self.panelParams.setParamGuess)
        self.connect(self,QtCore.SIGNAL("showPanelParams"),self.panelParams.show)
        self.connect(self,QtCore.SIGNAL("fitFailled"),self.panelParams.fitFailled)
        
#    @classmethod
    def showPanelParams(self):
        """displays a panel for easy fit parameter initialization"""
        #import Qt_FitterParams
        if self.panelParams == None:
            return
        self.emit(QtCore.SIGNAL("showPanelParams"))
        
    def getParamsFromPanel(self):
        self.param_guess = dict()
        for i in self.PARAMS:
            self.param_guess[i] = self.panelParams.getGuessVal(i)
            
        
        
@registerFit
class FitterCosPlusLin(Fitter):
    """fits a cosine on top of a linear background, for the moment only for small slopes
    y=offset+slope*x+a*cos(2*pi*x0*x+phi)"""
    ID_STR = "CosPlusLin"
    PARAMS = [__OFFSET__,__AMPL__,__X0_HZ__,__PHI__,__SLOPE__]
    def guessParam(self):
        X=self.Xdata
        Y=self.Ydata

        x=numpy.fft.fftfreq(len(X),X[1]-X[0])
        y=numpy.fft.fft(Y)

        offset=abs(y[0])/len(X)
        xt=x[1:len(X)/2]
        yt=y[1:len(X)/2]

        nmax=numpy.argmax(abs(yt))
        x0=xt[nmax]
        slope=0
        a=2*max(abs(yt))/len(X)
        phi=numpy.arctan(numpy.imag(yt[nmax])/numpy.real(yt[nmax]))-(numpy.sign(numpy.real(yt[nmax]))-1.0)/2*numpy.pi
        return {__OFFSET__:offset,__AMPL__:a,__X0_HZ__:x0,__PHI__:phi,__SLOPE__:slope}
        
    def func(self,X,par):
        return par[0]+par[4]*X+par[1]*numpy.cos(2*numpy.pi*par[2]*X+par[3])


@registerFit
class FitterCos(Fitter):
    """fits a cosine"""
    ID_STR = "Cos"
    PARAMS = [__OFFSET__,__AMPL__,__X0_HZ__,__PHI__]
    def guessParam(self):
        X=self.Xdata
        Y=self.Ydata

        x=numpy.fft.fftfreq(len(X),X[1]-X[0])
        y=numpy.fft.fft(Y)

        offset=abs(y[0])/len(X)
        xt=x[1:len(X)/2]
        yt=y[1:len(X)/2]

        nmax=numpy.argmax(abs(yt))
        x0=xt[nmax]

        a=2*max(abs(yt))/len(X)
        phi=numpy.arctan(numpy.imag(yt[nmax])/numpy.real(yt[nmax]))-(numpy.sign(numpy.real(yt[nmax]))-1.0)/2*numpy.pi
        return {__OFFSET__:offset,__AMPL__:a,__X0_HZ__:x0,__PHI__:phi}
        #print(offset)

    def guessParamsFromCursors(self,x1,y1,x2,y2):
        self.param_guess = {__OFFSET__:1,__AMPL__:2,__X0_HZ__:3,__PHI__:4}

    def func(self,X,par):
        return par[0]+par[1]*numpy.cos(2*numpy.pi*par[2]*X+par[3])


class FitterPeakedFunc(Fitter):
    """generic class for fitting peaked functions (lorentz gauss ...)
    needing to guess a center amplitude and width"""
    PARAMS = [__GAMMA_HZ__,__X0_HZ__,__AREA__,__OFFSET__]

    def guessParam(self):
        """ gives initial guess for amplitude, x_0, width of the peak in Y(X)
        return format : (FWHM,X0,a,offset)
        """
        X = self.Xdata
        Y = self.Ydata
        iMax = Y.argmax()

        x_0  = X[iMax]
        a    = Y[iMax]

        HWHM_left = -1
        HWHM_right= -1
        offset = Y.mean()
        a = a-offset
        for index in range(iMax,len(X)):
            if Y[index]<=offset+a/2:
                FWHM = X[index] - x_0
            break
        if HWHM_right==-1:
            HWHM_right = X[index] - x_0
        for index in range(iMax,0,-1):
            if Y[index]<=offset+a/2 :
                HWHM_left = x_0 - X[index]
                break
        if HWHM_left ==-1:
            HWHM_left = x_0 - X[index]

        FWHM = HWHM_left + HWHM_right
        if FWHM == 0:
            FWHM = (X[len(X)-1]-X[0])/10

        # convert a to area
        a = a*math.pi*FWHM/2
        return {__GAMMA_HZ__:FWHM,__X0_HZ__:x_0,__AREA__:a,__OFFSET__:offset}


    def guessParamsFromCursors(self,x1,y1,x2,y2):
        """cursor 1 should indicate the frequency of the peak to fit"""
        x0_hz = x1
        X = self.Xdata
        Y = self.Ydata
        for k,x in enumerate(self.Xdata):
            if x0_hz < x:
                iMax = k
                break

       # iMax = Y.argmax()

        x_0  = X[iMax]
        a    = Y[iMax]

        HWHM_left = -1
        HWHM_right= -1
        offset = Y.mean()
        a = a-offset
        for index in range(iMax,len(X)):
            if Y[index]<=offset+a/2:
                FWHM = X[index] - x_0
            break
        if HWHM_right==-1:
            HWHM_right = X[index] - x_0
        for index in range(iMax,0,-1):
            if Y[index]<=offset+a/2 :
                HWHM_left = x_0 - X[index]
                break
        if HWHM_left ==-1:
            HWHM_left = x_0 - X[index]

        FWHM = HWHM_left + HWHM_right
        if FWHM == 0:
            FWHM = (X[len(X)-1]-X[0])/10

        # convert a to area
        a = a*math.pi*FWHM/2
        self.param_guess = {__GAMMA_HZ__:FWHM,__X0_HZ__:x_0,__AREA__:a,__OFFSET__:offset}


  #  def unpackParam(self,par):
  #      self.param_fitted = {__GAMMA_HZ__:par[0],__X0__:par[1],__AREA__:par[2],__OFFSET__:par[3]}

    #def interactiveGuess(self,x0_hz = 0):
    #    """ gives initial guess for amplitude around x_0 given, width of the peak in Y(X)
    #    return format : (FWHM,X0,a,offset)
    #    """


    def outputPar(self):
        self.saveFp(sys.stdout)

    def unpackParam(self,par):
        super(FitterPeakedFunc,self).unpackParam(par)
        self.param_fitted[__GAMMA_HZ__] = abs(self.param_fitted[__GAMMA_HZ__])

def lorentz(par,X):
    gam = par[0]
    x_0 = par[1]
    a = par[2]
    if len(par)>=4:
        offset = par[3]
    else :
        offset = 0
    return 1/math.pi*(a*abs(gam)/2)/((X-x_0)*(X-x_0)+gam**2/4)+offset





@registerFit
class FitterLorentz(FitterPeakedFunc):
    ID_STR = "Lorentz"
    """class to fit lorentzians"""
   #@staticmethod
   #def func(self,par):
    #    return lorentz(par,self.Xdata)

    def func(self,X,par):
        return lorentz(par,X)

#   def fitString(self):
#      return LORENTZ


#   def plot(self,clear = False,**kwds):
 #      cl = clear
  #     p = Fitter.plot(self,clear = cl,**kwds)
      # p.set_label("fit lorentz : Q=%1.1f" %(self.param_fitted[__X0__]/self.param_fitted[__GAMMA_HZ__]))

class FitterDoublePeakedFunc(FitterPeakedFunc):
    PARAMS = [__GAMMA_HZ__,__X0_HZ__,__AREA__,__OFFSET__,__GAMMA_2_HZ__,__X0_2__,__AREA_2__]


    def guessParamsFromCursors(self,x1,y1,x2,y2):
        """cursor 1(2) should indicate frequency and height of the lorentzian(Gaussian)"""

        X = self.Xdata
        Y = self.Ydata
        offset = Y.min()

        amplLor = y1-offset
        amplGauss = y2-offset

        for k,x in enumerate(self.Xdata):
            if x1 < x:
                iMax = k
                break

       # iMax = Y.argmax()

        x_0  = X[iMax]

        HWHM_left = -1
        HWHM_right= -1
        offset = Y.mean()

        for index in range(iMax,len(X)):
            if Y[index]<=offset+amplLor/2:
                FWHM = X[index] - x_0
            break
        if HWHM_right==-1:
            HWHM_right = X[index] - x_0
        for index in range(iMax,0,-1):
            if Y[index]<=offset+amplLor/2 :
                HWHM_left = x_0 - X[index]
                break
        if HWHM_left ==-1:
            HWHM_left = x_0 - X[index]

        FWHM = HWHM_left + HWHM_right
        if FWHM == 0:
            FWHM = (X[len(X)-1]-X[0])/10

        # convert a to area
        a = amplLor*math.pi*FWHM/2
        FWHM_Lor =FWHM


        for k,x in enumerate(self.Xdata):
            if x2 < x:
                iMax = k
                break

       # iMax = Y.argmax()

        x_0  = X[iMax]

        HWHM_left = -1
        HWHM_right= -1
        offset = Y.mean()

        for index in range(iMax,len(X)):
            if Y[index]<=offset+amplGauss/2:
                FWHM = X[index] - x_0
            break
        if HWHM_right==-1:
            HWHM_right = X[index] - x_0
        for index in range(iMax,0,-1):
            if Y[index]<=offset+amplGauss/2 :
                HWHM_left = x_0 - X[index]
                break
        if HWHM_left ==-1:
            HWHM_left = x_0 - X[index]

        FWHM = HWHM_left + HWHM_right
        if FWHM == 0:
            FWHM = (X[len(X)-1]-X[0])/10

        # convert a to area
        a2 = amplGauss*math.pi*FWHM/2
        FWHM_Gauss =FWHM



        return {__GAMMA_HZ__:FWHM_Lor,__GAMMA_2_HZ__:FWHM_Gauss,__X0_HZ__:x1,__X0_2__:x2,__AREA__:a,__AREA_2__:a2,__OFFSET__:offset}


@registerFit
class FitterDoubleLorentz(FitterDoublePeakedFunc):
    #PARAMS = [__GAMMA_HZ__,__X0_HZ__,__AREA__,__OFFSET__,__GAMMA_2_HZ__,__X0_2__,__AREA_2__]
    ID_STR = "doubleLorentz"


    def func(self,X,par):
        return lorentz(par[:4],X)+lorentz(par[4:],X) ##attention temporary gauss


    def guessParam(self):
        """looks for 2 positive peaks of around the same width. first one is simply searched for at the maximum of the curve"""
        self.fitterAnnex = FitterLorentz()
        self.fitterAnnex.Xdata = self.Xdata
        self.fitterAnnex.Ydata = self.Ydata
        self.fitterAnnex.fit(verboseLevel = 0,param_fixed = {__X0_HZ__:self.Xdata[self.Ydata.argmax()]})
        self.residu = self.Ydata-self.fitterAnnex.Y
        self.residucum = pylab.cumsum(self.residu)

#        left = self.Xdata[self.residucum.argmax()]
#       right = self.Xdata[self.residucum.argmin()]

        ### find the largest increase of residucum on an interval of FWHM(first peak)
        x0 = self.Xdata[0]
        FWHM1 = self.fitterAnnex.param_fitted[__GAMMA_HZ__]
        for i,x in enumerate(self.Xdata):
            if abs(x-x0)>abs(FWHM1):
                discreteWidth = i
                break
        discreteWidth = discreteWidth/2 #this might help when the guess is to wide
        if discreteWidth==0:
            discreteWidth = 1
        vals = self.residucum[discreteWidth:]-self.residucum[:-discreteWidth]
        x0_2 = self.Xdata[vals.argmax()+discreteWidth/2]

        FWHM2 = FWHM1
#        x0_2 = (left+right)/2
 #       FWHM2 = abs(right-left)/5
        a2 = vals.max()*FWHM2/5
        param_guess = self.fitterAnnex.param_guess
        param_guess[__X0_HZ__] = self.fitterAnnex.param_fixed[__X0_HZ__]

        param_guess[__OFFSET__] = 0 #no offset
        param_guess[__GAMMA_2_HZ__] = param_guess[__GAMMA_HZ__]#FWHM2
        param_guess[__X0_2__] = x0_2
        param_guess[__AREA_2__] = a2

        return param_guess

    def unpackParam(self,par):
        super(FitterDoubleLorentz,self).unpackParam(par)
        self.param_fitted[__GAMMA_HZ__] = abs(self.param_fitted[__GAMMA_HZ__])
        self.param_fitted[__GAMMA_2_HZ__] = abs(self.param_fitted[__GAMMA_2_HZ__])

@registerFit
class FitterDoubleLorentzNeg(FitterDoubleLorentz):
    ID_STR = "doubleLorentzNeg"
    def guessParam(self):
        self.Ydata = -self.Ydata
        param_guess = FitterDoubleLorentz.guessParam(self)
        param_guess[__OFFSET__] = -param_guess[__OFFSET__]
        param_guess[__AREA__] = -param_guess[__AREA__]
        param_guess[__AREA_2__] = -param_guess[__AREA_2__]
        self.Ydata = -self.Ydata
        return param_guess

def gauss(par,X):
    sigma=par[0]/(2*math.sqrt(math.log(2)*2))
    x_0=par[1]
    a = par[2]
    if len(par)>=4:
        offset = par[3]
    else :
        offset = 0
    return a/(sigma*math.sqrt(2*math.pi))*numpy.exp(-(X-x_0)*(X-x_0)/(2*sigma**2))+offset




@registerFit
class FitterGauss(FitterPeakedFunc):
    ID_STR = "Gauss"
    """class to fit Gaussians"""
    def func(self,X,par):
        return gauss(par,X)


@registerFit
class FitterLorentzAndGauss(FitterDoublePeakedFunc):
    """class to fit lorentzians + calibration peak"""
    ID_STR = LORENTZ_GAUSS
    PARAMS = [__GAMMA_HZ__,__X0_HZ__,__AREA__,__OFFSET__,__GAMMA_2_HZ__,__X0_2__,__AREA_2__]

    debugFlagGaussOnRight = True
    def func(self,X,par):
       return lorentz(par[:4],X)+gauss(par[4:],X)

    def fitString(self):
       return LORENTZ_GAUSS






    def guessParam(self):
        """will first call the function FitPeakedFunc.guessParam(self) on the left half of the spectrum then on the right and merge the results together"""
        Xbackup = numpy.copy(self.Xdata)
        Ybackup = numpy.copy(self.Ydata)
        self.Xdata = Xbackup[:len(Xbackup)*3/4]
        self.Ydata = Ybackup[:len(Ybackup)*3/4]
        par1 = FitterPeakedFunc.guessParam(self)
        

        self.Xdata = Xbackup[len(Xbackup)*3/4:]
        self.Ydata = Ybackup[len(Ybackup)*3/4:]
        par2 = FitterPeakedFunc.guessParam(self)
        


        self.Xdata = Xbackup
        self.Ydata = Ybackup

        # assign gaussian to smaller width (calibration peak)

        #oneIsLorentz =(par1[__GAMMA_HZ__]>par2[__GAMMA_HZ__])
        #if(par1[__AREA__]/par1[__GAMMA_HZ__] > 10*par2[__GAMMA_HZ__]/par2[__GAMMA_HZ__]):###calibration peak is some noise on the lorentzian
         #   1/0
          #  oneIsLorentz = False

        #if(par2[__AREA__]/par2[__GAMMA_HZ__] > 10*par1[__GAMMA_HZ__]/par1[__GAMMA_HZ__]):
         #   1/0
          #  oneIsLorentz = True
        if self.debugFlagGaussOnRight:
            oneIsLorentz = par1[__X0_HZ__]<par2[__X0_HZ__]


        if (oneIsLorentz):
            param_guess = par1
            param_guess[__GAMMA_2_HZ__] = par2[__GAMMA_HZ__]
            param_guess[__X0_2__] = par2[__X0_HZ__]
            param_guess[__AREA_2__] = par2[__AREA__]#(par2[:3])
        else :
            param_guess = par2
            param_guess[__GAMMA_2_HZ__] = par1[__GAMMA_HZ__]
            param_guess[__X0_2__] = par1[__X0_HZ__]
            param_guess[__AREA_2__] = par1[__AREA__]#(par1[:3])

        return param_guess

    def unpackParam(self,par):
        super(FitterLorentzAndGauss,self).unpackParam(par)
        self.param_fitted[__GAMMA_HZ__] = abs(self.param_fitted[__GAMMA_HZ__])
        self.param_fitted[__GAMMA_2_HZ__] = abs(self.param_fitted[__GAMMA_2_HZ__])
        self.param_fitted[__AREA_2__] = abs(self.param_fitted[__AREA_2__])


#    def unpackParam(self,par):
 #       self.fitted_param = {__GAMMA_HZ__:par[0],__X0__:par[1],__AREA__:par[2],__OFFSET__:par[3],__GAMMA_2_HZ__:par[4],__X0_2__:par[5],__AREA_2__:par[6]}

#    def saveFp(self,fp):
 #       c = ConfigParser.ConfigParser()
  #
   #     c.add_section(__FIT_TYPE__)
    #    c.set(__FIT_TYPE__,__TYPE__,self.fitString())

     #   c.add_section(__FIT_PARAMETERS__)
      #  c.set(__FIT_PARAMETERS__,__GAMMA_HZ__,self.param_fitted[0])
       # c.set(__FIT_PARAMETERS__,__X0__,self.param_fitted[1])
        #c.set(__FIT_PARAMETERS__,__AREA__,self.param_fitted[2])
  #      c.set(__FIT_PARAMETERS__,__OFFSET__,self.param_fitted[3])
   #
    #    c.set(__FIT_PARAMETERS__,__GAMMA_2_HZ__,self.param_fitted[4])
     #   c.set(__FIT_PARAMETERS__,__X0_2__,self.param_fitted[5])
      #  c.set(__FIT_PARAMETERS__,__AREA_2__,self.param_fitted[6])
       # c.write(fp)



#    def outputPar(self):
#        self.saveFp(sys.stdout)
#       print(__GAMMA_HZ__    + " = " + str(self.param_fitted[0])
  #      print(__X0__          + " = " + str(self.param_fitted[1])
   #     print(__AREA__        + " = " + str(self.param_fitted[2])
    #    print(__OFFSET__      + " = " + str(self.param_fitted[3])

#    def plot(self,clear = False):
 #      cl = clear
 #      p = Fitter.plot(self,clear = cl)
#    def unpackParam(self,par):
 #       super(FitterPeakedFunc,self).unpackParam(par)
  #      self.param_fitted[__GAMMA_HZ__] = abs(self.param_fitted[__GAMMA_HZ__])

    def makeLabel(self):
        return "fit lor.+gauss : Q=%f" %(self.param_fitted[1]/self.param_fitted[0])

@registerFit
class FitterLinear(Fitter):
    """class to fit linear"""
    ID_STR = "Linear"
    PARAMS = [__SLOPE__,__OFFSET__]
    def func(self,X,par):
       return par[0]*X + par[1]

    def guessParam(self):
       return {__SLOPE__:0,__OFFSET__:0}
   
@registerFit
class FitterPoly2(Fitter):
    """class to fit second order poly"""
    ID_STR = "Poly2"
    PARAMS = ["a","a","c"]
    def func(self,X,par):
       return par[0]*X**2 + par[1]*X + par[2]

    def guessParam(self):
       return {"a":1,"b":1,"c":1}
       
@registerFit
class FitterButter1(Fitter):
    """class to fit butterworth filter"""
    ID_STR = "Butter1"
    PARAMS = ["a0","a1"]
    def func(self,X,par):
       return numpy.log(par[0]/(1.0+par[1]*X**2))

    def guessParam(self):
       return {"a0":1.0e-4,"a1":1e-16}
       
@registerFit
class FitterButter2(Fitter):
    """class to fit butterworth filter"""
    ID_STR = "Butter2"
    PARAMS = ["a0","a1","a2"]
    def func(self,X,par):
       return numpy.log(par[0]/(1.0+par[1]*X**2+par[2]*X**4))

    def guessParam(self):
       return {"a0":1.0e-4,"a1":1e-16,"a2":1e-32}
       
@registerFit
class FitterButter3(Fitter):
    """class to fit butterworth filter"""
    ID_STR = "Butter3"
    PARAMS = ["a0","a1","a2","a3"]
    def func(self,X,par):
       return numpy.log(par[0]/(1.0+par[1]*X**2+par[2]*X**4+par[3]*X**6))

    def guessParam(self):
        return {"a0":1.0e-4,"a1":1e-16,"a2":1e-32,"a2":1e-45}


@registerFit
class FitterButterTry(Fitter):
    """class to fit butterworth filter"""
    ID_STR = "ButterTry"
    PARAMS = ["a0","a1_","a1","a2_","a2","a3_","a3"]
    def func(self,X,par):
       return numpy.log(par[0]/(1.0+par[1]*X,par[2]*X**2+par[3]*X**3+par[4]*X**4 + par[5]*X**5 +par[6]*X**6  ))

    def guessParam(self):
       return {"a0":1.0e-4,"a1":1e-16,"a2":1e-32,"a2":1e-45}



class FitterMultiple(Fitter):
    """class to fit multiple dataset"""
    def __init__(self,name = "multiFit",parameters = None,parentCurve1=None,parentCurve2=None,**kwds):
        n = name
        super(FitterMultiple,self).__init__(name = n,**kwds)
        self.iterNr = 0
        self.parentCurve1 = parentCurve1
        self.parentCurve2 = parentCurve2
        self.Xdata = numpy.concatenate((parentCurve1.X,parentCurve2.X))
        self.Ydata = numpy.concatenate((parentCurve1.Y,parentCurve2.Y))
        self.middle = len(parentCurve1.X)

        self.curve1 = plotting.Plottable(parentCurve = parentCurve1,X = parentCurve1.X,Y = parentCurve1.Y,name = n)
        self.curve2 = plotting.Plottable(parentCurve = parentCurve2,X = parentCurve2.X,Y = parentCurve2.Y,name = n)

    def Xdata1(self):
        return self.Xdata[:self.middle]

    def Xdata2(self):
        return self.Xdata[self.middle:]

    def Ydata1(self):
        return self.Y[:self.middle]

    def Ydata2(self):
        return self.Xdata[self.middle:]


    def setXdata1(self,X1):
        self.curve1.X = X1
        self.Xdata = numpy.concatenate((X1,self.Xdata2()))
        self.middle = len(X1)


    def setXdata2(self,X2):
        self.curve2.X = X2
        self.Xdata = numpy.concatenate((self.Xdata1(),X2))


    def func(self,par):
        return numpy.concatenate((self.func1(par),self.func2(par)))

    def plot(self,*args,**kwds):
        back1 = self.curve1.X
        back2 = self.curve2.X

        back = self.Xdata
        backMiddle = self.middle
#        self.curve1.X = numpy.arange(self.curve1.X.min(),self.curve1.X.max(),1000)
        X1 = numpy.arange(self.curve1.X.min(),self.curve1.X.max(),1000)
        self.setXdata1(X1)
        self.curve1.Y = self.func1(self.packParams())

        X2 = numpy.arange(self.curve2.X.min(),self.curve2.X.max(),1000)
        self.setXdata2(X2)
        self.curve2.Y = self.func2(self.packParams())

        self.curve1.plot(*args,**kwds)
        self.curve2.plot(*args,**kwds)

        self.Xdata = back
        self.middle = backMiddle

       # self.curve1.X = back1
       # self.curve2.X = back2

       # self.getYvalues(self.packParams())

    def plotGuess(self,*args,**kwds):
        backupX = self.curve1.X
        backupY = self.curve1.Y
        self.curve1.Y = self.func1(self.packParamsGuess())
        Plottable.plot(self.curve1,*args,**kwds)
        self.curve1.Y = backupY

        backupX = self.curve2.X
        backupY = self.curve2.Y
        self.curve2.Y = self.func2(self.packParamsGuess())
        Plottable.plot(self.curve2,*args,**kwds)
        self.curve2.Y = backupY


    def getYvalues(self,par):
        Fitter.getYvalues(self,par)
        (self.curve1.X,self.curve1.Y) = (self.X[:self.middle],self.Y[:self.middle])
        (self.curve2.X,self.curve2.Y) = (self.X[self.middle:],self.Y[self.middle:])

class FitterSpring(FitterMultiple):
    __POWER__ = "power"
    __KAPPA_HZ__ = "kappa_hz"
    __SPLIT_HZ__ = "split_hz"
    ID_STR = "basicSpring"
    PARAMS = [__GAMMA_HZ__,__X0_HZ__,__KAPPA_HZ__,__SPLIT_HZ__,__POWER__]
    def func1(self,par):
        X = self.Xdata1()-par[3]/2
        return par[0]+dataAnalysis.deltaGamma(X,par[2],par[3],par[4])
    def func2(self,par):
        X = self.Xdata2()-par[3]/2
        return par[1]+dataAnalysis.deltaOmega(X,par[2],par[3],par[4])


    def guessParam(self):
        return {__GAMMA_HZ__ : 18e6,__X0_HZ__ : 52e6, self.__KAPPA_HZ__ : 5e6,self.__SPLIT_HZ__ : 20e6,self.__POWER__ : 10e6}



class FitterSpringWithT(FitterMultiple):
    __T0__    = "T0"
    __POWER__ = "power"
    __KAPPA_HZ__ = "kappa_hz"
    __SPLIT_HZ__ = "split_hz"
    __HEATING_COEFF__ = "heating_coeff"
    __DELTA_0__ = "delta0"
    ID_STR = "springWithT"
    PARAMS = [__T0__,__X0_HZ__,__KAPPA_HZ__,__SPLIT_HZ__,__POWER__,__HEATING_COEFF__]



    def T(self,par):
        """returns the temperature at point X as a function of fit parameters"""
        X = self.Xdata1()-par[3]/2
        return par[0]+par[5]*TLS.deltaTresonant(X,par[2],par[3],par[4])



    def func1(self,par):
        X = self.Xdata1()-par[3]/2
        T = self.T(par)
        invQ = TLS.invQ(T)
        Gamma_hz = 52e6*invQ
        return numpy.real(Gamma_hz+dataAnalysis.deltaGamma(X,par[2],par[3],par[4]))

    def func2(self,par):
        X = self.Xdata2()-par[3]/2
        T = self.T(par)
        df = TLS.df(T)
        return numpy.real(par[1]+df+dataAnalysis.deltaOmega(X,par[2],par[3],par[4]))

    def guessParam(self):
        return {self.__T0__ : 0.86,__X0_HZ__ : 51.84e6,self.__KAPPA_HZ__ : 5e6,self.__SPLIT_HZ__ : 20e6,self.__POWER__ : 10e6,self.__HEATING_COEFF__ : 1e9}


class FitterSpringWithTadim(FitterMultiple):
    __T0__    = "T0"
    __POWER__ = "power"
    __KAPPA_HZ__ = "kappa_hz"
    __SPLIT_HZ__ = "split_hz"
    __HEATING_COEFF__ = "heating_coeff"
    __DELTA_0__ = "delta0"
    ID_STR = "springWithTadim"
    PARAMS = [__T0__,__X0_HZ__,__KAPPA_HZ__,__SPLIT_HZ__,__POWER__,__HEATING_COEFF__]

    def T(self,par):
        """returns the temperature at point X as a function of fit parameters"""
        X = self.Xdata1()-par[3]/2
        return par[0]+par[5]*1e15*TLS.deltaTresonant(X,par[2],par[3],par[4])

    def func1(self,par):
        X = self.Xdata1()-par[3]/2
        T = self.T(par)
        invQ = TLS.invQ(T)#1.0/TLS.QClamp + TLS.invQres(T) + TLS.invQrelax(T) -(TLS.invQres(par[0])+ TLS.invQrelax(par[0]))
        Gamma_hz = invQ*SampleConstants.fm
        return numpy.real(Gamma_hz+dataAnalysis.deltaGamma(X,par[2],par[3],par[4]))

    def func2(self,par):
        X = self.Xdata2()-par[3]/2
        T = self.T(par)
        df = TLS.df(T)-TLS.df(par[0])
        return numpy.real(par[1]+df+dataAnalysis.deltaOmega(X,par[2],par[3],par[4]))

    def guessParam(self):
        return {self.__T0__ : 0.8,__X0_HZ__ : 0,self.__KAPPA_HZ__ : 15e6,self.__SPLIT_HZ__ : 30e6,self.__POWER__ : 10e6,self.__HEATING_COEFF__ : 1e16}

    def plotT(self):
        plotting.plot(self.Xdata1(),self.T(self.packParams()),win = "Temperature",name = "T")

    def plotTLSinvQ(self,*args,**kwds):
        par = self.packParams()
        T = self.T(par)
        TLSinvQ = TLS.invQres(T)+ TLS.invQrelax(T) -(TLS.invQres(par[0])+ TLS.invQrelax(par[0]))
        gamma_hz = TLSinvQ*SampleConstants.fm
        plotting.plot(self.Xdata1(),gamma_hz,name = "invTLSQ",*args,**kwds)

    def plotTLSdf(self,*args,**kwds):
        par = self.packParams()
        T = self.T(par)
        df = (TLS.df(T)-TLS.df(par[0]))*SampleConstants.fm
        plotting.plot(self.Xdata1(),df,name = "TLSdf",*args,**kwds)

@registerFit
class FitterSplittedNA(Fitter):
    ID_STR = "splittedNA"
    PARAMS = ["delta_hz","pin_mw","eta","omega_m_hz","gamma_m_hz","scaling","gamma","g0","kappa_hz"]
    def func(self,X,par):
        return formulaNA.splittedNAmW(X,*par)
    
    def guessParam(self):
#        self.param_guess =  {"delta_hz":-24e6,"abar":100,"eta":0.5,"Omega_m_hz":70e6,"Gamma_m_hz":1e4,"scaling":1,"g0":1,"gamma":10e6,"kappa_hz":10e6}        
        X = self.Xdata
        Y = self.Ydata
        
        temp = plotting.DimArray(Y,X)
        w = self.getParamAnyVal("omega_m_hz")
        temp.removeSegmentX(w-2e6,w+2e6)
        X = numpy.asarray(temp.X)
        Y = numpy.asarray(temp.Y)
        
        iMax = Y.argmax()

        x_0  = X[iMax]
        a    = Y[iMax]
        
       
        
        
        HWHM_left = -1
        HWHM_right= -1
        offset = Y.mean()
        a = a-offset
        for index in range(iMax,len(X)):
            if Y[index]<=offset+a/2:
                FWHM = X[index] - x_0
            break
        if HWHM_right==-1:
            HWHM_right = X[index] - x_0
        for index in range(iMax,0,-1):
            if Y[index]<=offset+a/2 :
                HWHM_left = x_0 - X[index]
                break
        if HWHM_left ==-1:
            HWHM_left = x_0 - X[index]

        FWHM = HWHM_left + HWHM_right
        if FWHM == 0:
            FWHM = (X[len(X)-1]-X[0])/10

        
        temp.removeSegmentX(x_0-0.5*self.getParamAnyVal("kappa_hz"),x_0+0.5*self.getParamAnyVal("kappa_hz"))
        X = numpy.asarray(temp.X)
        Y = numpy.asarray(temp.Y)
        
        iMax = Y.argmax()
        x_0_2  = X[iMax]
        g = self.getParamAnyVal("gamma")
        if(x_0_2 > x_0):
            x_0 = x_0+g/2
        else:
            x_0 = x_0-g/2
        # convert a to area
        return {"kappa_hz":FWHM*3,"delta_hz":-x_0,"scaling":a}



#class FitterOptSpectrum(FitterDoubleLorentz):
#    def GuessParam(self):
#        self.Ydata = -self.Ydata
#        FitterDoubleLorentz.GuessParam(self)
#        self.Ydata = -self.Ydata
#        self.param_guess[__AREA__] = -self.param_guess[__AREA__]
#        self.param_guess[__AREA_2__] = -self.param_guess[__AREA_2__]
#        self.param_guess[__OFFSET__] = -self.param_guess[__OFFSET__]


#    def GetDeltaSB(self):
#        x1 = self.parentCurve.getWin().getXvalue()



#FitterLorentz.registerClass()
#FitterGauss.registerClass()
#FitterDoubleLorentz.registerClass()
#FitterDoubleLorentzNeg.registerClass()
#FitterLorentzAndGauss.registerClass()
#FitterCos.registerClass()
#FitterCosPlusLin.registerClass()

#fitter[LORENTZ] = FitterLorentz
#fitter[GAUSS] = FitterGauss
#fitter[FitterDoubleLorentz.ID_STR] = FitterDoubleLorentz
#fitter[FitterLorentzAndGauss.ID_STR] = FitterLorentzAndGauss
print "Fit imported"
