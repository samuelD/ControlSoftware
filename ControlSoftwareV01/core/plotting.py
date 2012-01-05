import pylab
import numpy
#import fit
import math
import scipy
from scipy import optimize
import sys
import ConfigParser
import loadSave
import utils
from utils import Unit
#import Qt_plot
#import Qt_plotManager

from PyQt4 import QtCore
#from PyQt4 import QtGui
import copy
import utils.Unit
from utils.Unit import IncompatibleUnitsError
import flags

def selectedCurve():
    try:
        return flags.plotManager.treeWidget.currentItem().ptrToParent
    except AttributeError:
        return None
    
       
def plot(*args,**kwds):
    """plots X against Y, returns a Fittable object constructed with the keywords arguments used..."""
    
    #first intercept kwds for Plottable.__init__ (I know it s dirty...)
    constructorKeys = Plottable.getConstructorKeys(kwds)
    
    if len(args)==0:
        return Fittable(plotKwds = kwds,**constructorKeys)
    
        
    try:
        y = args[1]
    except IndexError:
        y = args[0]
        x = range(len(y))
        args = args[1:]
    else:
        if isinstance(y,list)or isinstance(y,numpy.ndarray):
            x = args[0]
            y = args[1]
            args = args[2:]
        else:
            y = args[0]
            x = range(len(y))
            args = args[1:]
    
    
    o = Fittable(X = x,Y = y,plotKwds = kwds,**constructorKeys)
    o.plot()
    return o

class plotter(QtCore.QObject):
    def __init__(self):
        QtCore.QObject.__init__(self)

#class Plotter(QtCore.QThread):
#    def __init__(self):
#        QtCore.QThread.__init__(self)
#        self.done = False
#    def run(self):
#        print "thread running"
#        self.plotManager = PlotManager()
#        self.done = True
#        self.exec_()






class DimArray(loadSave.Saveable):
    __SECTION__ = "DIMENSIONS"
    __unit_x__ = "unit_x"
    __unit_y__ = "unit_y"
    __name_x__ = "name_x"
    __name_y__ = "name_y"
    """a 2D array with dimensions"""
    def __init__(self,Y = None,X = None,unit_y = 1,unit_x = 1,name_y = None,name_x = None,tags = None):
        self.X = X
        self.Y = Y
        self.unit_x = unit_x
        self.unit_y = unit_y
        self.tags = tags

        if (X == None)and(Y==None):
            self.X = []
            self.Y = []
        else:
            if X==None:
                self.Y = numpy.array(Y)
                self.X = numpy.array(range(0,len(Y)))
            else:
                if Y == None:
                    self.X = numpy.array(X)
                    self.Y = numpy.zeros(len(X))
                else:
                    self.X = numpy.array(X)
                    self.Y = numpy.array(Y)


        if isinstance(unit_x,basestring):
            unit_x = Unit.unitFromStr(unit_x)
        if isinstance(unit_y,basestring):
            unit_y = Unit.unitFromStr(unit_y)

        if unit_x is None:
            unit_x = 1
        if unit_y is None:
            unit_y = 1
        self.unit_x = unit_x
        self.unit_y = unit_y


        if name_y == None:
            name_y = Unit.getName(self.unit_y)
            if name_y == "":
                name_y = "Y"
        if name_x == None:
            name_x = Unit.getName(self.unit_x)
            if name_x == "":
                name_x = "X"

        self.name_y = name_y
        self.name_x = name_x

    def toSIUnits(self):
        self.convert_x(Unit.SIunit(self.unit_x))
        self.convert_y(Unit.SIunit(self.unit_y))
        return self

    def set_unit_y(self,newUnit):
        self.unit_y = newUnit
    def set_unit_x(self,newUnit):
        self.unit_x = newUnit

    def convert_x(self,newUnit):
        """converts the x axis of the array (changes the numerical values) into the newUnit if compatible"""
        fact = Unit.inUnit(self.unit_x,newUnit)
        self.X = self.X*fact
        self.unit_x = newUnit

    def convert_y(self,newUnit):
        """converts the y axis of the array (changes the numerical values) into the newUnit if compatible"""
        if self.unit_y is Unit.dBm:
            if Unit.isUnit(newUnit,Unit.W):
                self.setXY(self.X,10**(self.Y/10)*0.001)
                self.set_unit_y(newUnit)
                return
            else:
                raise IncompatibleUnitsError(Unit.dBm,newUnit)
        fact = Unit.inUnit(self.unit_y,newUnit)
        self.Y = self.Y*fact
        self.unit_y = newUnit


    def getYSpan(self):
        return abs(self.Y.min()-self.Y.max())
    def getXSpan(self):
        return abs(self.X.min()-self.X.max())
    def getYrange(self):
        return [self.Y.min(),self.Y.max()]
    def getXrange(self):
        return [self.X.min(),self.X.max()]

    def getAppropriateUnitX(self):
        ran = max(self.X) - min(self.X)
        if ran != 0:
            unitUp = int(numpy.log10(ran))/3
            new_u = Unit.upgradeUnit(self.unit_x,unitUp)
        else:
            new_u = self.unit_x
        return new_u


    def getAppropriateUnitY(self):
        ran = max(self.Y) - min(self.Y)
        if ran != 0:
            unitUp = int(numpy.log10(ran))/3
            new_u = Unit.upgradeUnit(self.unit_y,unitUp)
        else:
            new_u = self.unit_y
        return new_u
        #self.convert_x(new_u)

    def __save__(self,f):
        self.toSIUnits()

        if self.tags != None:
            X = []
            Y = []
            T = []
            for (x,y,t) in zip(self.X,self.Y,self.tags):
                X.append("%.9g"%x)
                Y.append("%.9g"%y)
                T.append(t)
            data = numpy.array([X,Y,T])
            format = "%s"
        else:
            data = numpy.array([self.X,self.Y])
            format = "%.9g"


        d = dict()
        d[DimArray.__unit_x__] = Unit.unitStr(self.unit_x)
        d[DimArray.__unit_y__] = Unit.unitStr(self.unit_y)
        d[DimArray.__name_x__] = self.name_x
        d[DimArray.__name_y__] = self.name_y

#        if self.tags != None:
 #           d[Plottable.__TAGS__] = self.tags
        c = ConfigParser.ConfigParser()
        utils.dict_CP.saveDictToConfParser(d,c,DimArray.__SECTION__)
        c.write(f)

        f.write("["+ Plottable.__DATA__ + "]\n")
        numpy.savetxt(f,data.transpose(),delimiter = ",",fmt = format)#,fmt = ["%.6g","%.6g","%s"])#,fmt = "%.9g")


    def __loadFromCP__(self,cp):
        d = utils.dict_CP.configParserToDict(cp,DimArray.__SECTION__)
        self.unit_x = Unit.unitFromStr(d[DimArray.__unit_x__])
        self.unit_y = Unit.unitFromStr(d[DimArray.__unit_y__])
        self.name_x = d[DimArray.__name_x__]
        self.name_y = d[DimArray.__name_y__]

    def __load_data__(self,f,logScale = False):
        """loads only the data (not contained in the configParser)"""
        pos = f.tell()
        t = numpy.loadtxt(f,delimiter = ",",usecols = [0,1])
        f.seek(pos)
        try:
            self.tags = numpy.loadtxt(f,delimiter = ",",usecols = [2],dtype = "string")
        except IndexError:
            pass
       #  try:
       #     w = cp.get(Plottable.__SECTION__,Plottable.__WIN__)
       # except ConfigParser.NoSectionError:
       #     w = "no name"
       # Plottable.__init__(self,win = w)
        if logScale == False:
            [self.X,self.Y] = t.transpose()
        else:
            [self.X,self.Ylog] = t.transpose()
            self.Y = utils.misc.dBmToVolts(self.Ylog)


    def setXY(self,X,Y):
        self.X = X
        self.Y = Y

    def truncateX(self,Xmax):
        X = []
        Y = []
        for x,y in zip(self.X,self.Y):
            if x <Xmax:
                X.append(x)
                Y.append(y)
        self.setXY(X,Y)
        
    def clipSegmentX(self,Xmin,Xmax):
        """remove data points between Xmin and Xmax"""
        X = []
        Y = []
        for x,y in zip(self.X,self.Y):
            if x<Xmax and x>Xmin:
                X.append(x)
                Y.append(y)
        self.setXY(X,Y)

    def removeSegmentX(self,Xmin,Xmax):
        """remove data points between Xmin and Xmax"""
        X = []
        Y = []
        for x,y in zip(self.X,self.Y):
            if x>Xmax or x<Xmin:
                X.append(x)
                Y.append(y)
        self.setXY(X,Y)


    def linInterp(self,x):
        """interpolate using the closest point and next one"""
        distX = abs(x-self.X)
        index1 = distX.argmin()
        index2 = index1+1
        X1 = self.X[index1]
        X2 = self.X[index2]
        Y1 = self.Y[index1]
        Y2 = self.Y[index2]
        return (Y1*(X2-x)+Y2*(x-X1))/(X2-X1)

    def mean(self,Xmin,Xmax):
        X = []
        Y = []
        for x,y in zip(self.X,self.Y):
            if x>Xmin and x<Xmax:
                X.append(x)
                Y.append(y)
        return numpy.array(Y).mean()

    def argMax(self):
        return self.X[self.Y.argmax()]

class Plottable(DimArray,QtCore.QObject):
    __EXT__ = "plt"
    __DATA__ = "DATA"
#    __PLOTTABLE__ = "PLOTTABLE"
    __WIN__  = "win"
    __TAGS__ = "tags"


    __SECTION__ = "PLOTTABLE"

    def __loadFromCP__(self,cp):
        d = utils.dict_CP.configParserToDict(cp,Plottable.__SECTION__)
        self.win = d[Plottable.__WIN__]
        DimArray.__loadFromCP__(self,cp)

    def __init__(self,Y = None,X = None,style = "-",unit_y = None,unit_x = None,name_y = None,name_x = None,tags = None,win = "no name",file = None,parentCurve = None,logScale = False,uncheckOthers = False,scaleOnMe = True,plotKwds = dict(),extra = dict(),**kwds):
        QtCore.QObject.__init__(self)#,parent = None)
        self.win = win
        self.plotKwds = plotKwds
        self.higlighted = False
        if parentCurve!= None:
            if unit_x == None:
                unit_x = parentCurve.unit_x
            if unit_y == None:
                unit_y = parentCurve.unit_y
        DimArray.__init__(self,Y,X,unit_y,unit_x,name_y,name_x,tags)

        self.setStyle(style)
        self.scaleOnMe = scaleOnMe
        self.tags = tags
        self.uncheckOthers=uncheckOthers

        self.parentCurve = parentCurve
        if parentCurve!=None:
            if (parentCurve.win != self.win)and(self.win!= "no name"):
                raise ValueError("if win is specified, it should be the same as parent's curve win!!!")
            self.win = parentCurve.win
        if file != None:
            self.__load_data__(file,logScale)
        loadSave.Saveable.__init__(self,extra = extra,**kwds)
        if flags.GUIon:
            self.connect(self, QtCore.SIGNAL("plot"), flags.plotManager.plot,QtCore.Qt.QueuedConnection)
            self.connect(self, QtCore.SIGNAL("remove"), flags.plotManager.remove,QtCore.Qt.QueuedConnection)
            self.connect(self, QtCore.SIGNAL("highlightItem"), flags.plotManager.setHighlighted)
        #plotManager.connect(plotManager, QtCore.SIGNAL("plotDone"),self.plotDone,QtCore.Qt.QueuedConnection)


    

    def plotDone(self):
        print "the plot was done"

    def appendPoint(self,Y = 0,X = None,tag = None):
        Y = float(Y)
        if X == None:
            X = len(self.X)
        if isinstance(self.X,numpy.ndarray):
            self.X = numpy.append(self.X,X)
            self.Y = numpy.append(self.Y,Y)
            print "appending data to a numpy array is very inefficient, try initializing your array with Y = []"
        else:
            self.X.append(X)
            self.Y.append(Y)

        if tag!= None:
            if self.tags == None:
                if len(self.X) == 1:
                    self.tags = [tag]
                else:
                    raise ValueError("cannot add a tag to a curve which allready contains untagged points")
            else:
                self.tags.append(tag)

    def toClipboardText(self):
        data = numpy.array([self.X,self.Y])
        import StringIO
        s = StringIO.StringIO()
        format = "%.9g"
        numpy.savetxt(s,data.transpose(),delimiter = "\t",fmt = format)
        return s.getvalue()
        
    def setHighlighted(self,bool):
        self.higlighted = bool
        self.emit(QtCore.SIGNAL("highlightItem"),self,bool)    
        
        
    def toArray(self):
        self.X = numpy.array(self.X)
        self.Y = numpy.array(self.Y)

 #   def delete(self):
 #       """removes properly all references to the curve"""
 #       win = self.getWin()

    def uncheck(self):
        self.treeItem.setCheckState(0,0)

    def check(self):
        self.treeItem.setCheckState(0,2)

    def addWinInManager(self):
        try:
            flags.plotManager.plots[self.win]
        except KeyError:
            from ..GUI.Qt_plot import Plot
            p = flags.plotManager.add_plot(Plot(name = self.win))


    def getXrangeLine(self):
        xd = self.line.get_xdata()
        return [xd.min(),xd.max()]

    def getYrangeLine(self):
        yd = self.line.get_ydata()
        return [yd.min(),yd.max()]
    
    def getXrangeLinePlusMargin(self):
        [m,M] = self.getXrangeLine()
        newMin = m-abs(m-M)*0.1
        if newMin<0 and m>=0:
            newMin = m*(1-0.3*numpy.sign(m))
        rpm = [newMin,M + abs(M-m)*0.1]
        return rpm

    def getYrangeLinePlusMargin(self):
        [m,M] = self.getYrangeLine()
        newMin = m-abs(m-M)*0.1
        if newMin<0 and m>=0:
            newMin = m*(1-0.3*numpy.sign(m))
        
        rpm = [newMin,M + abs(M-m)*0.1]#[,M*(1 + 0.3*numpy.sign(M))]
        return rpm

    def __save__(self,f):

        d = dict()
        d[Plottable.__WIN__] = self.win
#        if self.tags != None:
 #           d[Plottable.__TAGS__] = self.tags
        c = ConfigParser.ConfigParser()
        utils.dict_CP.saveDictToConfParser(d,c,Plottable.__SECTION__)
        c.write(f)

        DimArray.__save__(self,f)

    def getChilds(self):
        win = self.getWin()
        ret = []
        if self.treeItem == None:
            return []
        for i in range(self.treeItem.childCount()):
            ret.append(self.treeItem.child(i).ptrToParent)
        return ret


    def remove(self):
        while flags.plotManager.plotDone==False:
            flags.app.processEvents()
        
        flags.plotManager.plotDone = False
        self.emit(QtCore.SIGNAL("remove"),self)
        
        while flags.plotManager.plotDone==False:
            flags.app.processEvents()
        #plotManager.mutex.lock()
        #plotManager.mutex.unlock()
        

    def removeOld(self):
        try:
            if self.treeItem == None:
                return None
        except AttributeError:
            return None
        for ch in self.getChilds():
            ch.remove()
        win = self.getWin()
        if self.parentCurve == None:
            win = self.getWin()
            win.treeItem.removeChild(self.treeItem)
        else:
            self.parentCurve.treeItem.removeChild(self.treeItem)
        try:
            self.line.remove()
            #win.canvas.ax.lines.remove(self.line)
        except (ValueError,AttributeError):
            pass

        if win.updateMode:
            # after removing a line, do
             # see http://www.mail-archive.com/matplotlib-users@lists.sourceforge.net/msg01453.html
            #ignore = True
            #for line in win.canvas.ax.lines:
             #   x = line.get_xdata()
              #  y = line.get_ydata()
              #  win.canvas.ax.dataLim.update_from_data(x, y, ignore)
            #ignore = False
            #l = win.canvas.ax.plot(x,y) ## don't ask me why there is no way to update graph without plotting something in it
  #          plotManager.mutex.lock()
            win.canvas.draw()
   #         plotManager.mutex.unlock()
           # l.remove()
        flags.plotManager.plotDone = True




        self.treeItem = None

    def saveCSV(self,filename):
        data = numpy.array([self.X,self.Y])
        numpy.savetxt(filename,data.transpose(),delimiter = ",",fmt = "%.9g")

#    def __newWindow__(self):
#        w = Qt_plot.Qt_plot()
#        Plottable.windows[self.win] = w
#        #self.canvas = w.widget.canvas
#        Plottable.plotManager.addWin(self.win)
#        w.show()
#        return w.widget.canvas

    def getCanvas(self):
        return flags.plotManager.plots[self.win].canvas

    def select(self):
        flags.plotManager.treeWidget.setCurrentItem(self.treeItem)

    def setStyle(self,style):
        self.style = style

    def setVisibility(self,visible):
        win = self.getWin()
        canvas = self.getCanvas()
        if visible == False:
            canvas.ax.lines.remove(self.line)
          #  canvas.ax.autoscale_view()
        else:
            canvas.ax.lines.append(self.line)
        if win.updateMode:
            canvas.draw()
            
    def getVisibility(self):
        if self.treeItem.checkState(0) == 0:
            return False
        return True

    def getWin(self):
        return flags.plotManager.plots[self.win]

    def setWin(self,win):
        self.win = win

    def setName(self,name):
        self.name = name
        try:
            self.line.set_label(self.name)
        except AttributeError:
            pass
    def setUncheckOthers(self,uncheckOthers):
        self.uncheckOthers = uncheckOthers


    def setXY(self,X,Y):
        self.X = X
        self.Y = Y

    @classmethod
    def getConstructorKeys(cls,kwds):
        constructorKeys = dict()
        utils.transferKeyValuePair(kwds,constructorKeys,"style")
        utils.transferKeyValuePair(kwds,constructorKeys,"unit_y")
        utils.transferKeyValuePair(kwds,constructorKeys,"unit_x")
        utils.transferKeyValuePair(kwds,constructorKeys,"name_y")
        utils.transferKeyValuePair(kwds,constructorKeys,"name_x")
        utils.transferKeyValuePair(kwds,constructorKeys,"tags")
        utils.transferKeyValuePair(kwds,constructorKeys,"win")
        utils.transferKeyValuePair(kwds,constructorKeys,"parentCurve")
        utils.transferKeyValuePair(kwds,constructorKeys,"scaleOnMe")
        utils.transferKeyValuePair(kwds,constructorKeys,"uncheckOthers")
        utils.transferKeyValuePair(kwds,constructorKeys,"name")
        utils.transferKeyValuePair(kwds,constructorKeys,"setSelected")
        utils.transferKeyValuePair(kwds,constructorKeys,"extra")
        
        return constructorKeys


    def updateFields(self,kwds):
        """pops out the kwds which represent a field of a plottable and updates self with it"""
        kwds = self.getConstructorKeys(kwds)
        try:
            name = kwds.pop("name")
        except KeyError:
            pass
        else:
            self.setName(name)   
        try:
            uncheckOthers = kwds.pop("uncheckOthers")
        except KeyError:
            pass
        else:
            self.setUncheckOthers(uncheckOthers)              
        try:
            style = kwds.pop("style")
        except KeyError:
            pass
        else:
            self.setStyle(style)
        
        try:
            win = kwds.pop("win")
        except KeyError:
            pass
        else:
            self.setWin(win)
        
        for i in kwds:
            self.__setattr__(i,kwds[i])
        
        
            


    def plot(self,**kwds):
        """possible kwds are :
        style = "+r"
        win = \"myWindow\"
        setSelected = False
        uncheckOthers = True
        name = \"myCurve\"
        """
        if flags.GUIon:
            while flags.plotManager.plotDone==False:
                flags.app.processEvents()
        
            flags.plotManager.plotDone = False
#        plotManager.mutex.lock()
        
        constructorKeys = self.getConstructorKeys(kwds)
        self.plotKwds.update(kwds)###remaining keywords should be used by plotting function
        if flags.GUIon:
            self.emit(QtCore.SIGNAL("plot"),self,constructorKeys)
        else:
            print "to pylab"
            import pylab
            pylab.plot(self.X,self.Y,*self.style,**self.plotKwds)
 #       plotManager.lock()
        if flags.GUIon:
            while flags.plotManager.plotDone==False:
                flags.app.processEvents()
            
    def getFFT(self,isPlot = True,name = None,win = "FFT",saveWithCurve = False,*args,**kwds):
        """takes a plottable and returns the discrete fourier transform as (magnitude, phase)"""
        """if isPlot = True, the magnitude is plotted; for the moment no particular window function has been introduced"""
        """the additional args and keywords will be passed to the constructor of the Fittable that will be returned"""
        if name == None:
            name = self.name + "_FFT"
        f_mag = Fittable(*args,win = win,name = name + "_mag",**kwds)
        f_phase = Fittable(*args,win = win,name = name + "_phase",**kwds)
        X = numpy.fft.fftshift(numpy.fft.fftfreq(len(self.X),abs(self.X[1]-self.X[0])))
        Y = numpy.fft.fftshift(numpy.fft.fft(self.Y))/len(self.X)
        Yphase = numpy.angle(Y)
        Ymag = abs(Y) 
        f_mag.setXY(X,Ymag)
        f_phase.setXY(X,Yphase)
        if isPlot:
            f_mag.plot()
        if saveWithCurve:
            f_mag.path = self.path
            f_phase.path = self.path
            f_mag.save()
            f_phase.save()
        return (f_mag,f_phase)

    def multiplyByPoly(self,*args):
        """with args = [a0,a1,a2...], aplies the correction Y->Y*(a0*x**n + a1*x**(n-1) + a2*x**(n-2)...)"""
        Y = args[0]*numpy.ones(len(self.X))
        X = self.X
        for coeff in args[1:]:
            Y = coeff + Y*X
        Y = Y*self.Y
        
        self.setXY(X,Y)
        
    def divideByPoly(self,*args):
        """with args = [a0,a1,a2...], aplies the correction Y->Y/(a0*x**n + a1*x**(n-1) + a2*x**(n-2)...)"""
        X = self.X
        Y = args[0]*numpy.ones(len(self.X))
        for coeff in args[1:]:
            Y = coeff + Y*X
        Y = self.Y/Y

        self.setXY(X,Y)
        
        
from loadSave import registerAsExtension   
@registerAsExtension
class Fittable(Plottable):
    __EXT__ = "spe"
    __FIT_MODEL__ = "FIT_MODEL"
    __MODEL__ = "model"
    __FIT_PARAMS__= "FIT_PARAMS"

#    def createFitterInstance(self,fitModel):
#        self.fitter = {fit.LORENTZ:fit.FitterLorentz,fit.GAUSS:fit.FitterGauss,fit.LORENTZ_GAUSS:fit.FitterLorentzAndGauss,fit.LINEAR:fit.FitterLinear}[fitModel](Xdata=self.X,Ydata=self.Y,parentCurve = self)
#       self.setXY(self.X,self.Y)

    ##to be able to access fit parameters through f["x0_hz"] for instance
    def __getitem__(self,item):
        return self.fitter.param_fitted[item]


    def __init__(self,usePanelParams = None, model="Lorentz",param_fitted = None,**kwds):
        #params = fit.fitter[model].popoutParams(param_fitted)
        import fit
        Plottable.__init__(self,**kwds)
        self.fitter = fit.fitter[model](parameters = param_fitted,usePanelParams = usePanelParams,parentCurve = self)
        

    def __loadFromCP__(self,cp):
        try:
            fm = utils.dict_CP.convertSmartly(cp.get(Fittable.__FIT_MODEL__,Fittable.__MODEL__))
        except ConfigParser.NoSectionError:
            print "no info found about fit"
            pass
        else:
            self.createFitterInstance(fm)
            self.fitter.param_fitted = utils.dict_CP.configParserToDict(cp,Fittable.__FIT_PARAMS__)
            self.fitter.fitDone = True

    def __load__(self,f,cp):
         Plottable.__load__(self,f,cp)
         Fittable.__loadFromCP__(self,cp)


    def __save__(self,f):
        if self.fitter.fitDone:
            cp = ConfigParser.ConfigParser()
            cp.add_section(Fittable.__FIT_MODEL__)
            cp.set(Fittable.__FIT_MODEL__,Fittable.__MODEL__,self.fitter.ID_STR)
            utils.dict_CP.saveDictToConfParser(self.fitter.param_fitted,cp,Fittable.__FIT_PARAMS__)
            cp.write(f)
        Plottable.__save__(self,f)

    def fittedVal(self,X):
        """if fitDone, returns the value of the fit function evaluated at X = X"""
        if self.fitter.fitDone:
            return self.fitter.func(X,self.fitter.packParams())
        else:
            return
    
    def setXY(self,X,Y):
        self.X = numpy.array(X)
        self.Y = numpy.array(Y)
        self.fitter.Xdata = self.X
        self.fitter.Ydata = self.Y


    def showPanelParams(self):
        self.fitter.showPanelParams()

    def fit(self,usePanelParams = None,model = None,plotAfterwards = True,excludeXRegion = None,**kwds):
        """fits the curve : if no model is specified, then uses the predifine self.fitter type to fit,
         otherwise, makes a new fitter instance with the appropriate type
         
         -model = "Lorentz","Gauss","LorentzGauss"...(see fit.py for the complete list)
         -excludeXRegion = [70e6,72e6] will exclude the corresponding region from the fit
         -plotAfterwards = True/False if you want to auto plot after the fit
         -paramGuess = {x0_Hz:1e6, ....} for initial guess
         -paramFixed = {x0_Hz:1e6, ....} for fixed params
         """
        if (model == None)or(self.fitter.ID_STR == model):
            self.fitter.resetData()
        else:
            #self.fitter.removeFromPM()
            import fit
            self.fitter = fit.fitter[model](parentCurve = self)
        
        if usePanelParams == True:
            self.fitter._usePanel_ = True
            self.showPanelParams()
        if usePanelParams == False:
            self.fitter._usePanel_ = False
        if usePanelParams == None:
            self.fitter._usePanel_ = None
    #        self.fitter.blockSignals(False)
      #  else:
     #       self.fitter.blockSignals(True)
        
        if excludeXRegion is not None:
            self.fitter.excludeXRegion(excludeXRegion[0],excludeXRegion[1])
    
        self.fitter.fit(**kwds)

        if plotAfterwards:
             self.plot()

    def isUsePanel(self):
        return self.fitter.isUsePanel()

    def getPanelGuess(self):
        return self.fitter.panelParams
    
    
    def convert_x(self,newUnit):
        #try:
        self.fitter.convert_x(newUnit)
        #except AttributeError:
         #   pass
        super(Fittable,self).convert_x(newUnit)

    def convert_y(self,newUnit):
        #try:
        self.fitter.convert_y(newUnit)
        #except AttributeError:
         #   pass
        super(Fittable,self).convert_y(newUnit)

    def set_unit_y(self,newUnit):
        #try:
        self.fitter.set_unit_y(newUnit)
        #except AttributeError:
         #   pass
        super(Fittable,self).set_unit_y(newUnit)

    def set_unit_x(self,newUnit):
        #try:
        self.fitter.set_unit_x(newUnit)
        #except AttributeError:
        #    pass
        super(Fittable,self).set_unit_x(newUnit)


    def setWin(self,win):
        self.win = win
        self.fitter.win = win

    def getResiduals(self):
        """returns array of Residuals if Data have already been fitted"""
        return self.fitter.getResiduals()

    def getRMSofResiduals(self):
        """returns RMS of Residuals if data have already been fitted"""
        return numpy.sqrt(numpy.var(self.getResiduals()))

    def getSNR(self):
        """returns SNR = max-min of fitted trace / RMS of Residuals"""
        return abs(self.fitter.getYSpan()/self.getRMSofResiduals())


    def plot(self,plotNiceFit = False,nPointsFit = 5e4,*args,**kwds):
        """win is the index of the figure to append plot
        newWin = True makes a new figure
        clear remove all other plots in the figure
        """
        try:
            self.label
        except AttributeError:
            try :
                self.label = self.name
            except AttributeError:
                self.label = "unsaved_spectrum"

       # cl = clear
        ret = Plottable.plot(self,*args,**kwds)
       # try:

        self.fitter.plot(setSelected = False,plotNicely=plotNiceFit,nicePlotNpoints = nPointsFit)#clear = False)
        #except AttributeError:
         #   print "no fit to display"
        #pylab.legend()
        return ret





#loadSave.Saveable.ext[Plottable.__EXT__] = Fittable #loading a plottable returns a fittable object
loadSave.Saveable.ext["csv"] = Fittable




print "plotting imported"
