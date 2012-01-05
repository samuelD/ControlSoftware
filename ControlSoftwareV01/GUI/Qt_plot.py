from __future__ import with_statement
import numpy as np
import sys
from PyQt4 import QtCore
from PyQt4 import QtGui
import os
from ..core import utils
from ..core.utils import Unit
from ..core import loadSave
from Qt_plotManager import plotManager

from UI_plot import Ui_MainWindow

def checkPlotDefaultsDir():
    if not os.path.exists(utils.path.getPlotDefaultDir()):
         os.mkdir(utils.path.getPlotDefaultDir())
         
checkPlotDefaultsDir()

class Qt_plot(QtGui.QMainWindow, Ui_MainWindow):
    MANUAL_SCALE = 0
    AUTOSCALE = 1
    SCALE_ON_LAST = 2
    
    flagLogLin = {True:"log",False:"linear"}
    color1 = "<font color=#FF0000>"
    color2 = "<font color=#990000>"
    color3 = "<font color=#990099>"
    def __init__(self, parent = None,name = "no name"):
        super(Qt_plot, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle(name)
        self.logscaleflag = False
        self.logscaleflag_x = False
        self.loglinbutton.setText("y->%s"%self.flagLogLin[not self.logscaleflag][:3])
        self.loglinbutton.clicked.connect(self.switchScaleY)
        
        
        self.loglinbutton_x.setText("x->%s"%self.flagLogLin[not self.logscaleflag][:3])
        self.loglinbutton_x.clicked.connect(self.switchScaleX)
        
        
        self.buttonLegend.clicked.connect(self.toggleLegend)
        self.buttonPrint.clicked.connect(self.savePrint)
        self.buttonMore.clicked.connect(self.toggleMore)
        
        #QtCore.QObject.connect(self.actionHelp,QtCore.SIGNAL('triggered()'),self.openHelp)

        self.connect(self,QtCore.SIGNAL('logFlagChangedY'),self.setScaleY)
        self.connect(self,QtCore.SIGNAL('logFlagChangedX'),self.setScaleX)
        
        self.x1_label.setText(self.color1+"x1 = "+"</font>")
        self.x2_label.setText(self.color2+"x2 = "+"</font>")
        
        self.y1_label.setText(self.color1+"y1 = "+"</font>")
        self.y2_label.setText(self.color2+"y2 = "+"</font>")
        
        self.diffx_label.setText(self.color3+"Dx = "+"</font>")
        self.diffy_label.setText(self.color3+"Dy = "+"</font>")
        
        self.isLegend = False
              
        import os
        defaultScale = self.SCALE_ON_LAST
        #self.scalePolicy = defaultScale
        self.showMore = True
        self.toggleMore()
        self.radioGroup = utils.misc.radioButtonGroup((self.radioButton_1,self.manualScale_clicked),(self.radioButton_2,self.autoscale_clicked),(self.radioButton_3,self.scaleOnLast_clicked))
        #self.radioGroup.set(defaultScale)
        #if  is not None:
#        self.setGeometry()
        
        
        
        self.positionLogger = positionLogger(self)
        self.setScalePolicy(defaultScale)
        self.setWindowIcon(QtGui.QIcon(os.path.join(utils.path.getIconDir(),"plotIcon4.png")))
        
        self.load()
        self.loglinbutton_x.clicked.connect(self.positionLogger.arm)
        self.loglinbutton.clicked.connect(self.positionLogger.arm)
        self.spinBox_last.valueChanged.connect(self.positionLogger.arm)
        
        #self.emit(QtCore.SIGNAL("logFlagChangedY"),self.logscaleflag)
        #self.emit(QtCore.SIGNAL("logFlagChangedX"),self.logscaleflag_x)

    def savePrint(self):    
        self.saveAsPdf(saveInAutoGenDir = False)
        
    def toggleMore(self):
        buttons = [self.buttonPrint,self.buttonLegend,self.loglinbutton,self.loglinbutton_x,self.radioButton_1,self.radioButton_2,self.radioButton_3,self.y1,self.y2,self.y1_label,self.y2_label,self.x1,self.x1_label,self.x2,self.x2_label,self.diffx,self.diffx_label,self.diffy,self.diffy_label,self.label,self.spinBox_last]
        self.showMore = not self.showMore    
        if self.showMore:
            for b in buttons:
                b.show()
                self.buttonMore.setText("<<")
        else:
            for b in buttons:
                b.hide()
                self.buttonMore.setText(">>")
            
    def toggleLegend(self):
        self.isLegend = not self.isLegend
        if self.isLegend:
            self.buttonLegend.setText("hide legend")
            self.showLegend()    
        else:
            self.buttonLegend.setText("make legend")
            self.getAxis().legend_ = None
            self.draw()
    def setScalePolicy(self,nr):
        self.positionLogger.arm()
        self.scalePolicy = nr
        self.radioGroup.set(nr)
    def setAutoscale(self):
        self.setScalePolicy(self.AUTOSCALE)
    def setScaleOnLast(self):
        self.setScalePolicy(self.SCALE_ON_LAST)
    def setScaleManual(self):
        self.setScalePolicy(self.MANUAL_SCALE)
    def getScalePolicy(self):
        return self.scalePolicy
    def isAutoScale(self):
        return self.scalePolicy == self.AUTOSCALE
    def isManualScale(self):
        return self.scalePolicy == self.MANUAL_SCALE
    def isScaleOnLast(self):
        return self.scalePolicy == self.SCALE_ON_LAST
        
    def manualScale_clicked(self):
        #print "manual"
        self.setScaleManual()
    
#    def autoscale_clicked(self):
        #print "auto clicked"
#       self.scalePolicy = self.AUTOSCALE
        
    def autoscale_clicked(self):
        self.setAutoscale()
        self.zoomOutFull()
        
    def scaleOnLast_clicked(self):
        self.setScaleOnLast()
        self.scaleOnLastCurve()
        #print "scaleOnLast clicked"

    def getFileName(self):
        return os.path.join(utils.path.getPlotDefaultDir(),self.name + ".cfg")

    def load(self):
        file = self.getFileName()
        try:
            if os.path.exists(file):
                with open(file,"r") as f:
                    try:
                        l = f.readline().rstrip()
                        l = l.split("=")[1]
                        l1 = int(l)
                        l = f.readline().rstrip()
                        l = l.split("=")[1]
                        l2 = int(l)
                        l = f.readline().rstrip()
                        l = l.split("=")[1]
                        l3 = int(l)
                        l = f.readline().rstrip()
                        l = l.split("=")[1]
                        l4 = int(l)
                        self.setGeometry(l1,l2,l3,l4)
                    except IndexError:
                        pass
                    try:
                        l = f.readline().rstrip()
                        l = l.split("=")[1]
                        self.setScalePolicy(int(l))
                    except IndexError:
                        pass
                    try:
                        l = f.readline().rstrip()
                        l = (l.split("=")[1]).strip()
                        self.logscaleflag_x = {"True":True,"False":False}[l]
                    except IndexError:
                        pass
                    try:
                        l = f.readline().rstrip()
                        l = (l.split("=")[1]).strip()
                        self.logscaleflag = {"True":True,"False":False}[l]
                    except IndexError:
                        pass
                    try:
                        l = f.readline().rstrip()
                        l = (l.split("=")[1]).strip()
                        self.setNLast(int(l))
                    except IndexError:
                        pass
                    
        except ValueError:
            return None

 #   def mouseReleaseEvent(self,event):
 #       pass

 #   def mouseMovesEvent(self,event):
 #       print "dropped"
    def moveEvent(self,event):
        self.positionLogger.arm()
#    def focusOutEvent(self,event):
#        print "lost focus"
    
    def resizeEvent(self,event):
        self.positionLogger.arm()
        
    def save(self):
        file = self.getFileName()
        g = self.geometry()
        with open(file,"w") as f:
            f.write("left = " + str(g.left()) + "\n")
            f.write("top = " + str(g.top()) + "\n")
            f.write("width = " + str(g.width()) + "\n")
            f.write("height = " + str(g.height()) + "\n")
            f.write("autoscale = " + str(self.getScalePolicy())+ "\n")
            f.write("scale_x = " + str(self.logscaleflag_x)+ "\n")
            f.write("scale_y = " + str(self.logscaleflag)+ "\n")
            f.write("show_last = " + str(self.nLast())+ "\n")

    def renew_cursor_indicators(self,x1,y1,x2,y2,unitX,unitY):
        if unitX=="1":
            unitX=""
        if unitY=="1":
            unitY=""
        self.x1.setText(self.color1+"%.7g"%x1+ unitX +"</font>")
        self.x2.setText(self.color2+"%.7g"%x2+ unitX +"</font>")
        
        self.y1.setText(self.color1+"%.7g"%y1+ unitY +"</font>")
        self.y2.setText(self.color2+"%.7g"%y2+ unitY +"</font>")
        
        self.diffx.setText(self.color3+"%.7g"%(x2-x1)+ unitX +"</font>")
        self.diffy.setText(self.color3+"%.7g"%(y2-y1)+ unitY +"</font>")

    def closeEvent(self,event):
        self.treeItem.setCheckState(0,0)

    def select_file(self):
	file = QtGui.QFileDialog.getOpenFileName()	
	
	if file:
            pass

    def switchScaleY(self):
        self.switchScaleXorY(True)

    def switchScaleX(self):
        self.switchScaleXorY(False)

    def switchScaleXorY(self,YorX = True):
        if YorX:
            self.logscaleflag = not self.logscaleflag
            self.setScaleY(self.logscaleflag)
        else:
            self.logscaleflag_x = not self.logscaleflag_x
            self.setScaleX(self.logscaleflag_x)
        
    
        
    def setScaleY(self,flag):
        self.widget.canvas.ax.set_yscale(self.flagLogLin[flag])
        self.loglinbutton.setText("y->%s"%self.flagLogLin[not flag][:3])
        self.widget.canvas.draw()
    def setScaleX(self,flag):
        self.widget.canvas.ax.set_xscale(self.flagLogLin[flag])
        self.loglinbutton_x.setText("x->%s"%self.flagLogLin[not flag][:3])
        self.widget.canvas.draw()
            

class positionLogger(QtCore.QTimer):
    ARMED = 1
    IDLE  = 0
    def __init__(self,win):
        QtCore.QTimer.__init__(self)
        self.state = self.IDLE
        self.timeout.connect(win.save)
        self.timeout.connect(self.disArm)
    
    def arm(self):
        if self.state == self.IDLE:
           self.state = self.ARMED
           self.start(1000)
                    
    def disArm(self):
        self.stop()
        self.state = self.IDLE
        
        




#    def resizeEvent(self,resizeEvent):
 #       print resizeEvent.oldSize()
  #      print resizeEvent.size()
 #       self.widget1.canvas.resize(resizeEvent.size().width(),resizeEvent.size().height()-60)
#        resizeEvent.setAccepted(False)




class Plot(Qt_plot):
    def __init__(self,name = "newPlot"):#,curves = None):
        from Qt_plotManager import plotManager
        #QtCore.QObject.__init__(self)
        self.updateMode = True
        self.firstCurve = True
        self.name = name
        self.treeItem = QtGui.QTreeWidgetItem([name])
        self.treeItem.setCheckState(0,2) ##checked
        self.treeItem.ptrToParent = self
        plotManager.add_plot(self)


        Qt_plot.__init__(self,name = self.name)
        self.connect(self, QtCore.SIGNAL("removePlot"), plotManager.removePlot,QtCore.Qt.QueuedConnection)
#        self.win = Qt_plot.Qt_plot(name = self.name)
#        self.win.ptrToParent = self
 #       self.canvas = self.win.widget.canvas #where to perform the plotting operations
        self.canvas = self.widget.canvas
        self.canvas.ptrToWin = self
        self.show()

    def getLastCurve(self):
        return self.getCurves()[-1]

    def scaleOnLastCurve(self):
        c = self.getLastCurve()
        self.scaleOnCurve(c)

    def scaleOnCurve(self,plottable):
        self.set_xylim(plottable.getXrangeLinePlusMargin(),plottable.getYrangeLinePlusMargin())


    def set_xlabel(self,label):
        self.canvas.ax.set_xlabel(label)
    def set_ylabel(self,label):
        self.canvas.ax.set_ylabel(label)

    def subplot(self,*args,**kwds):
        self.canvas.subplot(*args,**kwds)
        self.canvas.draw()

    def getAxis(self):
        return self.canvas.fig.axes[0]
    
    def draw(self):
        self.canvas.draw()

    def showLegend(self):
        self.canvas.ax.legend()
        self.canvas.draw()

    def getCurves(self):
        ret = []
        for i in range(self.treeItem.childCount()):
            ret.append(self.treeItem.child(i).ptrToParent)
        return ret

    def hasUnit_x(self):
        try:
            self.unit_x
        except AttributeError:
            return False
        return True
    def hasUnit_y(self):
        try:
            self.unit_y
        except AttributeError:
            return False
        return True

    def dealWithUnits(self,plottable):
        """sets its own units the same as the plottable if they are undefined
        or *CONVERTS* the plottable in it's own units!!"""
        if self.hasUnit_x():
            Unit.checkCompatible(self.unit_x,plottable.unit_x)
        else:
            self.unit_x = plottable.getAppropriateUnitX()
        if self.hasUnit_y():
            Unit.checkCompatible(self.unit_y,plottable.unit_y)
        else:
            self.unit_y = plottable.getAppropriateUnitY()#plottable.unit_y

    def x_in_SI_units(self,xdata):
        return Unit.asNum(Unit.toSI(self.unit_x*xdata))
    def y_in_SI_units(self,ydata):
        return Unit.asNum(Unit.toSI(self.unit_y*ydata))

    def nLast(self):
        return self.spinBox_last.value()
    
    def setNLast(self,val):
        self.spinBox_last.setValue(val)

    def renew_curve(self,plottable):
        ### add a treeItem only if it doesn t has allready its own
        
        self.dealWithUnits(plottable)
        plotManager.remove(plottable)
        if self.nLast() > 0:
            try:
                self.getCurves()[-self.nLast()-1].uncheck()
            except IndexError:
                pass
        if plottable.uncheckOthers:
            plotManager.uncheckAll(plottable.getWin())
        plottable.treeItem = QtGui.QTreeWidgetItem([plottable.name,plottable.dateStr()])
        plottable.treeItem.setCheckState(0,2) #checked
        plottable.treeItem.ptrToParent = plottable #handle to the interesting object
        if plottable.parentCurve == None:
            self.treeItem.addChild(plottable.treeItem)
        else:
            plottable.parentCurve.treeItem.addChild(plottable.treeItem)
        
        if plottable.higlighted:
            plotManager.setHighlighted(plottable,plottable.higlighted)
        
        return plottable


    def setVisibility(self,visible):
        if visible:
            self.show()
        else:
            self.close()

    def remove(self):
        self.emit(QtCore.SIGNAL("removePlot"),self)

    def removeOld(self):
        self.update = False
        curves = self.getCurves()
        for c in curves:
            c.remove()
        plotManager.plots.pop(self.name)
        self.setVisibility(False)
        plotManager.treeWidget.removeItemWidget(self.treeItem,0)
        self.treeItem = None
        #del self
        

    def get_xylim(self):
        return (self.canvas.ax.get_xlim(),self.canvas.ax.get_ylim())

    def zoomOutFull(self):
        (xlim,ylim) = self.get_largest_xylimPlusMargin()
        self.set_xylim(xlim,ylim)

    def get_largest_xylimPlusMargin(self):
        l = self.getCurves()
        if len(l) == 0:
            return None
        for p in l:
            if p.getVisibility():
                [newXmin,newXmax] = p.getXrangeLinePlusMargin()
                [newYmin,newYmax] = p.getYrangeLinePlusMargin()
                break
        for p in l:
            sub = p.getChilds()
            sub.append(p)
            for pp in sub:
                if pp.getVisibility():
                    [xmin,xmax] = pp.getXrangeLinePlusMargin()
                    [ymin,ymax] = pp.getYrangeLinePlusMargin()
                    newXmax = max(newXmax,xmax)
                    newXmin = min(newXmin,xmin)
                    newYmax = max(newYmax,ymax)
                    newYmin = min(newYmin,ymin)
        return ([newXmin,newXmax],[newYmin,newYmax])
    def set_xylim(self,xlim = None,ylim = None):
        self.canvas.set_xylim(xlim,ylim)

    def saveAsPdf(self,name = None,path = None,saveInAutoGenDir = True,multipagePdf = None,openFile = True):
        """if a multipagePdf object is provided, will append the plot to a new page of the pdf object"""
        if name == None:
            name = self.name
        if path == None:
            if saveInAutoGenDir:
                path = loadSave.getCurrentDir()
                import os
                file = os.path.join(path,name)
            else:
                from PyQt4.QtGui import QFileDialog
                fd = QFileDialog()
                file = fd.getSaveFileName()
        else:
            import os
            file = os.path.join(path,name)

        if file[-4:]!=".pdf":
            file = file + ".pdf"

    
        if multipagePdf == None:
            from matplotlib.backends.backend_pdf import PdfPages
            pdf = PdfPages(file)
        else:
            pdf = multipagePdf
        pdf.savefig(self.canvas.fig)
        if multipagePdf == None:
            pdf.close()
        import os
        os.startfile(file)