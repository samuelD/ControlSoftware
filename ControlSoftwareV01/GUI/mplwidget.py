from ..core import plotting,fit
from ..core import utils
from ..core.utils import Unit
import time
import threading
import numpy
import copy
#import readConfig

from PyQt4 import QtGui,QtCore
from matplotlib.widgets import Cursor

from matplotlib.backends.backend_qt4agg \
import FigureCanvasQTAgg as FigureCanvas

#from matplotlib.backends.backend_qt4agg \
#import NavigationToolbar2QTAgg as NavigationToolbar

#availableFits = ["Lorentz","Gauss"]


debug = 1

class myActionFit(QtGui.QAction):
    def __init__(self,name,parent):
        QtGui.QAction.__init__(self,name,parent)
        self.fitType = name
        self.parent = parent
    def fit(self):
        self.parent.fitWithCursors(model = self.fitType)
        
    def _actionHovered(self):
            tip =  self.toolTip()
            QtGui.QToolTip.showText(QtGui.QCursor.pos(), tip)

from matplotlib.figure import Figure
class MplCanvas(FigureCanvas):
    def __init__(self,useblit = True):
        self.currentFitType = None
        #self.fitWithCursors = dict()
        #self.fitIt = dict()
       # for f in fit.fitter:
       #     pass
            #eval("""def fitWithCursors():
             #           c = self.getCurrentCurve()
             #           c.fit(model = \"Lorentz\")""")
        #for f in fit.fitter:
        #    setAttr(self,"currentFitModel",)
        #    def fitIt():
        #        c = self.getCurrentCurve()
        #        c.fit(model = f)
        #        print "fitting " + f
        #    self.fitWithCursors[f] = copy.deepcopy(fitIt)
        #    self.fitWithCursors[f].fun = f
        
        self.useblit = useblit
        self.needclear = False
        self.fig = Figure()
        self.lastLimits = [] # to store the last limits of zooms
        self.ax = self.fig.add_subplot(111)
        self.ax.set_autoscale_on(False)
        self.xSelected = False
    
       
        self.cursorActive = None
        self.cursorsVisible = False
        self.cursors = []
        self.cursors.append(MyCursor(0,0,self.ax, useblit=True, color='red', linestyle = "dashed",linewidth=1))
        self.cursors.append(MyCursor(0,0,self.ax, useblit=True, color='brown', linestyle = "dashed",linewidth=1))
        self.cursorsInitialized = False
        
        self.x = 0
        self.y = 0
        self.xdata = 0
        self.ydata = 0


        self.background = None

        FigureCanvas.__init__(self, self.fig)
        FigureCanvas.setSizePolicy(self,
                                   QtGui.QSizePolicy.Expanding,
                                   QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        
        
        
        
        

        self.mpl_connect('button_press_event', self.registerCoords) 
        self.mpl_connect('button_release_event', self.deactivateCursor) 
        self.mpl_connect('motion_notify_event', self.onmove)
        self.mpl_connect('draw_event', self.clear)
        self.mpl_connect('draw_event', self.displayCursors)
        self.mpl_connect('pick_event',self.picked)

        self.draw()
        import time
        time.sleep(0.1)
        self.repaint()
    
    def getLastCurve(self):
        w = self.ptrToWin
        return w.getCurves()[-1]
        #w = self.ptrToWin
        #print "OK"
        #return w.getCurves()[-1]
            
    
    def fitWithCursors(self,model = "Lorentz"):
        c = self.getCurrentCurve()
        w = self.ptrToWin
        x1 = w.x_in_SI_units(self.cursors[0].xdata)
        y1 = w.y_in_SI_units(self.cursors[0].ydata)
        x2 = w.x_in_SI_units(self.cursors[1].xdata)
        y2 = w.y_in_SI_units(self.cursors[1].ydata)
        c.fit(model = model,cursorVal = [x1,y1,x2,y2],plotAfterwards = True)
       
    def picked(self,event):
        curve = event.artist.ptrToParent
        x = event.mouseevent.xdata
        indexPoint = abs(curve.X-x).argmin()
        print curve.tags[indexPoint]

    def deactivateCursor(self,event):
        self.cursorActive = None
        #self.draw()

    def registerCoords(self,event):
        #self.xSelected = True
        self.lastMplEvent = event
        x = event.xdata
        y = event.ydata
        if x is None or y is None:
            return
        self.xdata = x
        self.ydata = y

        dist = []
        
        if event.button!=1:
            return

        if self.cursorsVisible:
            for c in self.cursors:                
                dist.append(utils.misc.distance((x,y),(c.xdata,c.ydata)))
            iMin = numpy.array(dist).argmin()
            self.setCursorActive(self.cursors[iMin])
            self.onmove(event)
                
            
               # if Utils.distance((x,y),(c.xdata,c.ydata))<max:
               #     self.setCursorActive(c)
               #     return
    
    def getCurrentCurve(self):
        c = plotting.selectedCurve()
        try:
            w = c.getWin()
        except AttributeError:
            return self.getLastCurve()
        if w!=self.ptrToWin:
            return self.getLastCurve()
            #print "the selected curve needs to be in the current plot..."
        return c
    


                
    def contextMenuEvent(self,event):
        self.lastEvent = event
        
        def setRangeDo():
            from ..hardware import hardwareDevices
            sp = []
            w = self.ptrToWin
            for c in self.cursors:
                sp.append(w.x_in_SI_units(c.xdata))
            hardwareDevices.defaultDevice("ESA").setRange(sp)

        setRange = QtGui.QAction("set range(default ESA)",self)
        setRange.triggered.connect(setRangeDo)

        def setFrequency():
            from ..hardware import hardwareDevices
            #c = plotting.selectedCurve()
            #x0 = c.getWin().x_in_SI_units(self.xdata)
            x0 = self.ptrToWin.x_in_SI_units(self.xdata)
            
            hardwareDevices.defaultDevice("FreqGen").setFreq(x0*Unit.Hz)
            hardwareDevices.defaultDevice("ESA").restart()
        setFreq = QtGui.QAction("set frequency(default FreqGen)",self)
        setFreq.triggered.connect(setFrequency)
        
        
#        def pickXvalue(message):
#            print message
#            self.xSelected = False
#            while not self.xSelected:
#                pass
#            print self.xdata
#            return (self.xdata,self.ydata)
#        def fitOptics():
#            x1 = pickXvalue("click on first sideband")[0]
#            x2 = pickXvalue("click on second sideband")[0]
#            c = plotting.selectedCurve()
#            c.fit(model = "doubleLorentzNeg"),#interactiveGuessParams = {"x0_hz":x1,"x0_2_hz":x2})
#            gamma1 = c["gamma_hz"]/abs(x2-x1)*200
#            gamma2 = c["gamma_2_hz"]/abs(x2-x1)*200
#            print "gamma1 = %f MHz"%gamma1
#            print "gamma2 = %f MHz"%gamma2


    

#        def fitLorentzHere():
#            c = self.getCurrentCurve()
#            if c is None:
#                return
#            x0 = c.getWin().x_in_SI_units(self.xdata)
#            c.fit(model = "Lorentz",interactiveGuessParams = {"x0_hz":x0})

 #       def fitGaussHere():
 #           c = self.getCurrentCurve()
 #           if c is None:
 #               return
 #           x0 = c.getWin().x_in_SI_units(self.xdata)
 #           c.fit(model = "Gauss",interactiveGuessParams = {"x0_hz":x0})    

        def zoomBack():
            w = self.ptrToWin
            if len(self.lastLimits)>0:
                (xlim,ylim) = self.lastLimits.pop()
            w.set_xylim(xlim,ylim)
        
        def zoomOut():
            w = self.ptrToWin
            (xlim,ylim) = w.get_xylim()
            dx = xlim[1]-xlim[0]
            dy = ylim[1]-ylim[0]
            (xlim,ylim) = ([xlim[0]-dx/2,xlim[1]+dx/2],[ylim[0] - dy/2,ylim[1] + dy/2])
            w.set_xylim(xlim,ylim)
            
        def zoomOutFull():
            self.ptrToWin.zoomOutFull()
        

        def zoomInCursorRegion():
            xlim = []
            ylim = []
            
#            c = plotting.selectedCurve()
            w = self.ptrToWin
            for c in self.cursors:
                xlim.append(c.xdata)
                ylim.append(c.ydata)
            xlim.sort()
            ylim.sort()
            w.set_xylim(xlim,ylim)
        menu = QtGui.QMenu(self)
        if self.cursorsVisible:
            zoomInCursorRegionAction = QtGui.QAction("zoom in cursor region",self)
            zoomInCursorRegionAction.triggered.connect(zoomInCursorRegion)
            menu.addAction(zoomInCursorRegionAction)
        else:
            showCursor = QtGui.QAction("show cursors",self)
            showCursor.triggered.connect(self.showCursor)
            menu.addAction(showCursor)
#        if self.lastLimits != []:
        zoomBackAction = QtGui.QAction("zoom back",self)
        zoomBackAction.triggered.connect(zoomBack)
        menu.addAction(zoomBackAction)
        
        zoomOutAction = QtGui.QAction("zoom out",self)
        zoomOutAction.triggered.connect(zoomOut)
        menu.addAction(zoomOutAction)
        
        zoomOutFullAction = QtGui.QAction("zoom out full",self)
        zoomOutFullAction.triggered.connect(zoomOutFull)
        menu.addAction(zoomOutFullAction)
        if self.cursorsVisible:
            hideCursor = QtGui.QAction("hide cursors",self) 
            hideCursor.triggered.connect(self.hideCursor)
            menu.addAction(hideCursor)

        menu.addAction(setFreq) 
        
        if self.cursorsVisible:
            menu.addAction(setRange)
        
        c = self.getCurrentCurve()#plotting.selectedCurve()


        if(isinstance(c,plotting.Fittable)):
            submenuFits = QtGui.QMenu(self)
            #submenuFits.addAction()
            for fitType in fit.fitter:
                #global currentFitType
                action = myActionFit(fitType,self)
                tip = fit.fitter[fitType].guessParamsFromCursors.__doc__
                if tip is None:
                    tip = "no help, sorry..."
                action.setToolTip(tip)
                action.triggered.connect(action.fit)
                action.hovered.connect(action._actionHovered)
                submenuFits.addAction(action)
            
          #  def contextMenuFits():
          #      menuFits = QtGui.QMenu(self)
          #      fitLorentz = QtGui.QAction("fit Lorentz (uses cursor 1)",self)
          #      fitLorentz.triggered.connect(fitLorentzHere)
          #      menuFits.addAction(fitLorentz)
          #      menuFits.exec_(event.globalPos())
            if self.cursorsVisible:
                fits = QtGui.QAction("cursor assisted fit of \"%s\""%c.name,self)
            #fits.hovered.connect(contextMenuFits)
                menu.addAction(fits)
                fits.setMenu(submenuFits)

            #fitLorentz = QtGui.QAction("fit Lorentz here (on \"%s\")!"%c.name,self)
            #fitLorentz.triggered.connect(fitLorentzHere)
            #menu.addAction(fitLorentz)
            
            #fitGauss   = QtGui.QAction("fit Gauss here (on \"%s\")!"%c.name,self)
            #fitGauss.triggered.connect(fitGaussHere)
            #menu.addAction(fitGauss)    
            
        #fitOpt = QtGui.QAction("fit optical oscillogramme",self)
        #t = threading.Thread(target = fitOptics)
        #fitOpt.triggered.connect(t.start)
        #menu.addAction(fitOpt) 
        menu.exec_(event.globalPos())
    
    def initializeCursors(self):
        #x = self.get_width_height()[0]/2
        #y = self.get_width_height()[1]/2
        xdiff = (self.ax.get_xbound()[0] - self.ax.get_xbound()[1])
        ydiff = (self.ax.get_ybound()[0] - self.ax.get_ybound()[1])
        for i,c in enumerate(self.cursors):
            c.setCoords(self.ax.get_xbound()[0]-xdiff*(i+1.0)/3,self.ax.get_ybound()[0]-ydiff*(i+1.0)/3)
        
    
    def showCursor(self):
        (x,y,xdata,ydata) = (self.lastMplEvent.x,self.lastMplEvent.y,self.lastMplEvent.xdata,self.lastMplEvent.ydata)
        self.cursorsVisible = True
        if not self.cursorsInitialized:
            self.initializeCursors()
            self.cursorsInitialized = True
        
        for c in self.cursors:
            c.visible = True
            c.linev.set_visible(c.visible and c.vertOn)
            c.lineh.set_visible(c.visible and c.horizOn)

        #self.draw()
        self.displayCursors()
        self.blit(self.ax.bbox)


    def hideCursor(self):
        self.cursorsVisible = False
        for c in self.cursors:
            c.visible = False
            c.linev.set_visible(c.visible and c.vertOn)
            c.lineh.set_visible(c.visible and c.horizOn)    
        self.draw()

    def setCursorActive(self,cursor):
        self.cursorActive = cursor
        

    def onmove(self, event):
        'on mouse motion draw the cursor if visible'
        if self.cursorActive == None:
            return
        #if event.inaxes != self.ax:
        #    self.cursorActive.linev.set_visible(False)
        #    self.cursorActive.lineh.set_visible(False)
            
        #if self.needclear:
        #    self.draw()
        #    self.needclear = False
        #return
        #self.needclear = True
        if event.inaxes != self.ax:
            return
        if not self.cursorActive.visible: return

        self.cursorActive.xdata = event.xdata
        self.cursorActive.ydata = event.ydata
        self.cursorActive.x = event.x
        self.cursorActive.y = event.y

        self.cursorActive.linev.set_xdata((event.xdata, event.xdata))
        self.cursorActive.lineh.set_ydata((event.ydata, event.ydata))
        self.cursorActive.linev.set_visible(self.cursorActive.visible and self.cursorActive.vertOn)
        self.cursorActive.lineh.set_visible(self.cursorActive.visible and self.cursorActive.horizOn)

        self.ptrToWin.renew_cursor_indicators(self.cursors[0].xdata,self.cursors[0].ydata,self.cursors[1].xdata,self.cursors[1].ydata,str(self.ptrToWin.unit_x),str(self.ptrToWin.unit_y))
        self._update()


    def displayCursors(self,other = None):
        for c in self.cursors:
            self.ax.draw_artist(c.linev)
            self.ax.draw_artist(c.lineh)
            
            
    def _update(self):
        # if self.cursorActive == None:
        #     return 
        if self.useblit:
            if self.background is not None:
                self.restore_region(self.background)
            self.displayCursors()
            # self.ax.draw_artist(self.cursorActive.linev)
            # self.ax.draw_artist(self.cursorActive.lineh)
            self.blit(self.ax.bbox)
        else:
            self.draw_idle()

        return False

    def clear(self, event):
        'clear the cursor'
        # if self.cursorActive != None:
        #     self.cursorActive.linev.set_visible(True)
        #     self.cursorActive.lineh.set_visible(False)
            
        if self.useblit:
            self.background = self.copy_from_bbox(self.ax.bbox)
        
        #self._update()

    def set_xylim(self,xlim =None,ylim = None):
        change = False
        self.lastLimits.append(self.ptrToWin.get_xylim())
        if xlim!=None:
            prevx = self.ax.get_xlim()
            if prevx!=xlim:
                change = True
                self.ax.set_xlim(xlim)
        if ylim!=None:
            prevy = self.ax.get_ylim()
            if prevy!=ylim:
                change = True
                self.ax.set_ylim(ylim)
        if change:
            for c in self.cursors:
                c.xdata = utils.misc.coerce(c.xdata,xlim)
                c.ydata = utils.misc.coerce(c.ydata,ylim)
            self.draw()

#    def resizeEvent(self,re):
#       self.resize(re.size().width(),re.size().height())


class MplWidget(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)
        self.canvas = MplCanvas()
        self.canvas.ptrToParent = self
        self.vbl = QtGui.QVBoxLayout()
    

        #  ntb = NavigationToolbar(self.canvas, self)
        # self.vbl.addWidget(ntb)
        self.vbl.addWidget(self.canvas)

        self.setLayout(self.vbl)
        



class MyCursor:
    def __init__(self,xdata,ydata, ax, useblit=False, **lineprops):
        """
        Add a cursor to ax.  If useblit=True, use the backend
        dependent blitting features for faster updates (GTKAgg only
        now).  lineprops is a dictionary of line properties.  See
        examples/widgets/cursor.py.
        """
        self.ax = ax
        self.canvas = ax.figure.canvas
        
#           self.canvas.mpl_connect('motion_notify_event', self.onmove)
#          self.canvas.mpl_connect('draw_event', self.clear)
         
        self.lineprops = lineprops   
        self.visible = True
        self.horizOn = True
        self.vertOn = True
        self.useblit = useblit
        
        
#        print ax.get_ybound()
    
        self.xdata = xdata
        self.ydata = ydata
    
        self.lineh = self.ax.axhline(self.ydata , visible=False, **self.lineprops)
        self.linev = self.ax.axvline(self.xdata , visible=False, **self.lineprops)
        
        self.setCoords(xdata,ydata)
        
        self.lineh.set_animated(True)
        self.linev.set_animated(True)
        #  self.background = None
        self.needclear = False
    
    def active(self):
        return self.canvas.cursorActive == self

    def setCoords(self,xdata,ydata):
        #self.x = x
        #self.y = y
        self.xdata = xdata
        self.ydata = ydata
        self.linev.set_xdata((xdata, xdata))
        self.lineh.set_ydata((ydata, ydata))
        
   
class DataCursor(Cursor):
    def __init__(self, ax, useblit=True, **lineprops):
        Cursor.__init__(self, ax, useblit=useblit,picker=5, **lineprops)
        #self.y = y
        #self.x = x
        self.xdata = self.canvas.xdata
        self.ydata = self.canvas.ydata
    
    def active(self):
        return self.canvas.cursorActive == self


    def drawFix(self,update = True):
        self.l1 = self.canvas.ax.plot([self.xdata,self.xdata],self.ax.get_ybound(),color = "red")
        self.l2 = self.canvas.ax.plot(self.ax.get_xbound(),[self.ydata,self.ydata],color = "red")
        if update:
            self.canvas.draw()
    def removeFix(self,update = True):
        self.canvas.ax.lines.remove(self.l1)
        self.canvas.ax.line.remove(self.l2)
        if update:
            self.canvas.draw()
    def getCoords(self,canvas):
        #self.y = canvas.y
        #self.x = canvas.x
        self.xdata = canvas.xdata
        self.ydata = canvas.ydata
     
    
    
    
    
    def clear(self,event):
        pass
    
    
    
    def onmove(self,event):
        #if self.active():
        if (event.button == 1):
            #self.y = event.y
            #self.x = event.x
            self.xdata = self.canvas.xdata
            self.ydata = self.canvas.ydata
            Cursor.onmove(self, event)
            

