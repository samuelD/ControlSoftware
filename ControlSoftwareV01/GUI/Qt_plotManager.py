#from __future__ import with_statement
#import numpy as np
#import sys
from .. import core
from ..core import loadSave
from PyQt4 import QtCore
from PyQt4 import QtGui
from ..core import utils
from ..core.utils import readConfig
from ..core.utils import Unit
from ..core import fit
from ..core import plotting

import os
#from ..core import plotting


from UI_plotManager import Ui_MainWindow


class Qt_plotManager(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None):
#        from ..core.utils import readConfig
        super(Qt_plotManager, self).__init__(parent)
        self.setupUi(self)
        self.treeWidget.setColumnWidth(0,300)
        self.treeWidget.setSelectionMode(3)
        self.treeWidget.setAlternatingRowColors(True)
        self.fileDialog = QtGui.QFileDialog()
        self.fileDialog.setDirectory(readConfig.defaultLoadDir())
        

        QtCore.QObject.connect(self.actionLoad, QtCore.
                               SIGNAL('triggered()'), self.load_file)

        QtCore.QObject.connect(self.actionLoad_multiple, QtCore.
                               SIGNAL('triggered()'), self.load_files)
#        QtCore.QObject.connect(self.actionLoad_dir, QtCore.
 #                              SIGNAL('triggered()'), self.load_dir)
        QtCore.QObject.connect(self.actionKill_all_windows, QtCore.
                               SIGNAL('triggered()'), self.killAllWindows)

        QtCore.QObject.connect(self.actionAbout_He3Control, QtCore.
                               SIGNAL('triggered()'), self.about)

        QtCore.QObject.connect(self.actionBugs,QtCore.SIGNAL('triggered()'),self.reportBug)
        QtCore.QObject.connect(self.actionHelp,QtCore.SIGNAL('triggered()'),self.openHelp)


        self.treeWidget.itemChanged.connect(self.itemChanged)

        self.setWindowIcon(QtGui.QIcon(os.path.join(utils.path.getIconDir(),"checkbox_icon2.gif")))
  
    def openHelp(self):
        import helpWins
        helpWins.help.show()

    def reportBug(self):
        mail = QtCore.QUrl("mailto:samuel.deleglise@epfl.ch?subject=bug report He3ControlV%s"%utils.path.version())
        QtGui.QDesktopServices.openUrl(mail)


    def about(self):
        import helpWins
        helpWins.about.show()

    def select_file(self):
        d = self.fileDialog
        if os.name == "posix":
            filename = str(d.getOpenFileName(directory = readConfig.defaultLoadDir()))
        else:
            filename = str(d.getOpenFileName())#))
        self.fileDialog.setDirectory(filename)
        return filename
    
    def select_files(self):
        d = self.fileDialog
        if os.name == "posix":
            filenamesU = d.getOpenFileNames(directory = readConfig.defaultLoadDir())
        else:
            filenamesU = d.getOpenFileNames()
        filenames = [str(i) for i in filenamesU]
        d.setDirectory(filenames[-1])
        return filenames
    
    def save_file(self):
        d = self.fileDialog
        if os.name == "posix":
            filenameU = d.getSaveFileName(directory = readConfig.defaultLoadDir())#))
        else:
            filenameU = d.getSaveFileName()
        filename = str(filenameU)
        return filename
    
    def killAllWindows(self):
        self.killAllWindows()

    def load_file(self):
        filename = self.select_file()
        if filename == "":
            print "no file selected"
            return
        loadable = loadSave.load(filename)
        loadable.plot()

    def load_files(self):
        filenames = self.select_files()
        loadable = loadSave.load(filenames)
        if filenames == []:
            print "no files selected"
            return
        l = loadable[0]
        l.plot()
        win = l.getWin()
        win.updateMode = False
        for i in loadable:
            i.plot()
        win.updateMode = True
        win.canvas.draw()


    def select_dir(self):
        d = QtGui.QFileDialog()
        dir = d.getExistingDirectory()
        return dir


    def addWin(self,name):
        item = QtGui.QTreeWidgetItem([name])
        self.treeWidget.addTopLevelItem(item)


    def itemChanged(self,item):
        visible = (item.checkState(0) == 2)        
        if item!= None:
            obj = item.ptrToParent
        else :
            return
        if isinstance(obj,plotting.Plottable): 
            for i in range(0,item.childCount()):
                ch =  item.child(i)
                ch.setCheckState(0,item.checkState(0))
        #if isinstance(item.ptrToParent,plotting.Plottable):
        item.ptrToParent.setVisibility(visible)
        #if isinstance(item.ptrToParent,plotting.Plot):
         #   item.ptrToParent.s

    def uncheckAll(self,plot = None):
        import Qt_plot
        if plot == False:
            plot = self.treeWidget.currentItem()
            if plot == None:
                return
            plot = plot.ptrToParent
            if not isinstance(plot,Qt_plot.Plot):
                plot = plot.getWin()
        plot.updateMode = False
        for curve in plot.getCurves():#plot.curves[i]
            curve.treeItem.setCheckState(0,0)
        plot.updateMode = True
        plot.canvas.draw()


    def runContextMenuPlot(self,event,plot):
        
        def uncheckAllChilds():
            plot.updateMode = False
            for curve in plot.getCurves():
                for cc in curve.getChilds():
                    cc.uncheck()
            plot.updateMode = True
            plot.canvas.draw()
        
        def checkAll():
            plot.updateMode = False
            for curve in plot.getCurves():
                curve.treeItem.setCheckState(0,2)
            plot.updateMode = True
            plot.canvas.draw()
        
        def killWindow():
            plot.remove()
            

        def saveAsPdf():
            plot.saveAsPdf(saveInAutoGenDir = False)

        menu = QtGui.QMenu(self)
        actionUncheckAll = QtGui.QAction("uncheck all",self)
        actionUncheckAll.triggered.connect(self.uncheckAll)

        actionUncheckAllChilds = QtGui.QAction("uncheck all childs",self)
        actionUncheckAllChilds.triggered.connect(uncheckAllChilds)

        actionCheckAll = QtGui.QAction("check all",self)
        actionCheckAll.triggered.connect(checkAll)

        actionKill = QtGui.QAction("kill window",self)
        actionKill.triggered.connect(killWindow)

        actionSaveAsPdf = QtGui.QAction("save as pdf",self)
        actionSaveAsPdf.triggered.connect(saveAsPdf)

        menu.addAction(actionUncheckAll)
        menu.addAction(actionCheckAll)
        menu.addAction(actionUncheckAllChilds)
        menu.addAction(actionKill)
        menu.addAction(actionSaveAsPdf)
        menu.exec_(event.globalPos())



    def runContextMenuCurve(self,event,plottable):
        def deleteCurve():
            plottable.remove()
        def uncheckAllButThis():
            plot = plottable.getWin()
            plot.updateMode = False
            for curve in plot.getCurves():#plot.curves[i]
                if curve!=plottable:
                    curve.treeItem.setCheckState(0,0)
            if plottable.treeItem.checkState(0)== 0:
                plottable.treeItem.setCheckState(0,2)
            plot.updateMode = True
            plot.canvas.draw()
        def saveCurve():
            filename = self.save_file()
            tab = os.path.split(filename)
            plottable.save(name = tab[1],path = tab[0])
        menu = QtGui.QMenu(self)
        
        def copyToClipBoard():
            from .. import app
            c = app.clipboard()
            c.setText(plottable.toClipboardText())
        
        
        
        fitter = None
        try:
            fitter = plottable.fitter
        except AttributeError:
            pass
        if isinstance(plottable,fit.Fitter):
            fitter = plottable
            
        if fitter is not None:
            actionDisplayFitParams = QtGui.QAction("display fit parameters",self)
            actionDisplayFitParams.triggered.connect(fitter.displayMeInPanel)
            menu.addAction(actionDisplayFitParams)
        
        actionCopyToClipboard = QtGui.QAction("copy data to clipboard",self)
        actionCopyToClipboard.triggered.connect(copyToClipBoard)
        
        actionRemove = QtGui.QAction("remove",self)
        actionRemove.triggered.connect(deleteCurve)
        
        actionSave = QtGui.QAction("save",self)
        actionSave.triggered.connect(saveCurve)

        actionUncheckAllButThis = QtGui.QAction("uncheck all but this",self)
        actionUncheckAllButThis.triggered.connect(uncheckAllButThis)


        menu.addAction(actionCopyToClipboard)
        menu.addAction(actionUncheckAllButThis)
        menu.addAction(actionSave)
        menu.addAction(actionRemove)
        menu.exec_(event.globalPos())



    def runContextMenuCurves(self,event,plottables):
        def deleteCurves():
            for p in plottables:
                p.remove()
        
        def uncheckAllChilds():
            plot = plottables[0].getWin()
            plot.updateMode = False
            for curve in plottables:
                for cc in curve.getChilds():
                    cc.uncheck()
            plot.updateMode = True
            plot.canvas.draw()
        
        def uncheckAllButThese():
            plot = plottables[0].getWin()
            plot.updateMode = False
            for curve in plot.getCurves():#plot.curves[i]
                if curve not in plottables:
                    curve.treeItem.setCheckState(0,0)
            for plottable in plottables:
                if plottable.treeItem.checkState(0)== 0:
                    plottable.treeItem.setCheckState(0,2)
            plot.updateMode = True
            plot.canvas.draw()
            
        def uncheckThese():
            plot = plottables[0].getWin()
            plot.updateMode = False
            for plottable in plottables:
                plottable.treeItem.setCheckState(0,0)
            plot.updateMode = True
            plot.canvas.draw()
            
        def checkThese():
            plot = plottables[0].getWin()
            plot.updateMode = False
            for plottable in plottables:
                plottable.treeItem.setCheckState(0,2)
            plot.updateMode = True
            plot.canvas.draw()
        
        
        menu = QtGui.QMenu(self)
        
        actionRemove = QtGui.QAction("remove",self)
        actionRemove.triggered.connect(deleteCurves)
        

        actionUncheckAllButThese = QtGui.QAction("uncheck all but these",self)
        actionUncheckAllButThese.triggered.connect(uncheckAllButThese)
        
        actionUncheckAllChilds = QtGui.QAction("uncheck all childs",self)
        actionUncheckAllChilds.triggered.connect(uncheckAllChilds)
        
        actionUncheckThese = QtGui.QAction("uncheck these",self)
        actionUncheckThese.triggered.connect(uncheckThese)
        
        
        actionCheckThese = QtGui.QAction("check these",self)
        actionCheckThese.triggered.connect(checkThese)

        menu.addAction(actionUncheckAllButThese)
        menu.addAction(actionCheckThese)
        menu.addAction(actionUncheckThese)
        menu.addAction(actionUncheckAllChilds)
        
        menu.addAction(actionRemove)
        menu.exec_(event.globalPos())
        
        
    
    def contextMenuEvent(self,event):
        import Qt_plot
        from ..core import plotting
        items = self.treeWidget.selectedItems()
        if items!=[]:
            if len(items)==1:
                obj = items[0].ptrToParent
                if isinstance(obj,Qt_plot.Plot):
                    self.runContextMenuPlot(event,obj) 
                if isinstance(obj,plotting.Plottable):
                    self.runContextMenuCurve(event,obj)
            else:
                obj = [item.ptrToParent for item in items]
                self.runContextMenuCurves(event,obj)
        else :
            return

        

   
      

class PlotManager(Qt_plotManager):#QtCore.QObject):
    def __init__(self):
#        QtCore.QObject.__init__(self)#,parent = None)
        Qt_plotManager.__init__(self)
        self.plotDone = True
        self.plots = dict()  #each of the items is a Plot
     #   self.frame = Qt_plotManager.Qt_plotManager()
     #   self.treeWidget = self.frame.treeWidget
      #  self.frame.show()
        self.show()
        self.mutex = QtCore.QMutex() ### an object to prevent multiple threads to do plotting at the same time
        
    def win(self,name):
        return self.plots[name]

    def curve(self,win,name):
        for curve in self.win(win).getCurves():
            if curve.name == name:
                return curve
#self.win(win).curves[name]

    def add_plot(self,plot):
        self.plots[plot.name] = plot
        self.treeWidget.addTopLevelItem(plot.treeItem)
        return plot

#    def hide(self):
 #       self.frame.hide()

    def getWindows(self):
        keyValues = self.plots.items()
        ret = []
        for i in keyValues:
            ret.append(i[1])
        return ret

    def killAllWindows(self):
        for i in self.getWindows():
            i.remove()
        

#    def show(self):
 #       self.frame.show()


    def removePlot(self,plot):
        print "removing plot"
        plot.update = False
        curves = plot.getCurves()
        for c in curves:
            c.remove()
        self.plots.pop(plot.name)
        plot.setVisibility(False)
#        self.treeWidget.removeItemWidget(plot.treeItem,0)
        self.treeWidget.takeTopLevelItem(self.treeWidget.indexOfTopLevelItem(plot.treeItem))
        plot.treeItem = None


    def setHighlighted(self,plottable,bool):
        try:
            treeItem = plottable.treeItem
        except AttributeError:
            return 
        if treeItem is None:
            return 
        
        self.treeWidget.blockSignals(True)
        if bool:
            treeItem.setTextColor(0,QtGui.QColor("blue"))
        else:
            treeItem.setTextColor(0,QtGui.QColor("black"))
        self.treeWidget.blockSignals(False)
    
    def remove(self,plottable):
        try:
            if plottable.treeItem == None:
                return None
        except AttributeError:
            return None
        for ch in plottable.getChilds():
            self.remove(ch)
        win = plottable.getWin()
        if plottable.parentCurve == None:
            win = plottable.getWin()
            win.treeItem.removeChild(plottable.treeItem)
        else:
            plottable.parentCurve.treeItem.removeChild(plottable.treeItem)
        try:
            plottable.line.remove()
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
            #plotManager.mutex.lock()
            win.canvas.draw()
            #plotManager.mutex.unlock()
           # l.remove()
        self.plotDone = True
        self.treeItem = None
        #plotManager.mutex.unlock()

    def plot(self,plottable,kwds):
        """plot plottable.Y vs plottable.X
        [options]:
        -same options as pylab.plot are available.
        -win = "toto" is the name of the figure to append plot to.
           if it doesnt allready exist a new figure is created
           If win = "p", then the plot is not appended to the plotManager but redirected to the pylab plotting system (a la matlab)
        - setSelected = False prevents the curve from being selected afterwards in plotManager
        """
#        print "should plot"
        #import
        #ToroidImport.app.processEvents()
        #self.mutex.lock()
        try:
            setSelected = False
            plottable.updateFields(kwds)
            if isinstance(plottable.X,list) or isinstance(plottable.Y,list):
                plottable.toArray()
            
            if plottable.win != "p":
                plottable.addWinInManager()
                try:
                    plottable.getWin().renew_curve(plottable)
                except Unit.IncompatibleUnitsError:
                    print "incompatible units detected, plottable will be routed towards a different window"
                    plottable.setWin(plottable.win + " " + Unit.unitStr(plottable.unit_y) + "(" + Unit.unitStr(plottable.unit_x)+")")
                    plottable.addWinInManager()
                    plottable.getWin().renew_curve(plottable)
                canvas = plottable.getCanvas()
                try:
                    self.plotInCanvas(plottable,plottable.getWin().unit_x,plottable.getWin().unit_y,canvas,**kwds)
                    if setSelected:
                        plottable.select()
                except:
                    self.remove(plottable)
                    raise
            else:
                import pylab
                pylab.plot(plottable.X,plottable.Y,plottable.style,label = plottable.name,**kwds)
                pylab.show()
        finally:
            self.plotDone = True
        
#        plotManager.mutex.unlock()
#        self.mutex.unlock()
#        self.emit(QtCore.SIGNAL("plotDone"),self)

    def plotInCanvas(self,plottable,unit_x,unit_y,canvas):
        canvas.ax.set_xlabel(plottable.name_x + " [" + Unit.unitStr(unit_x) + "]")
        canvas.ax.set_ylabel(plottable.name_y + " [" + Unit.unitStr(unit_y) + "]")
        plottable.line = canvas.ax.plot(plottable.X*Unit.inUnit(plottable.unit_x,unit_x),plottable.Y*Unit.inUnit(plottable.unit_y,unit_y),plottable.style,**plottable.plotKwds)[-1]
        plottable.line.ptrToParent = plottable

        w = plottable.getWin()
        if w.updateMode:
            if w.isScaleOnLast() and plottable.scaleOnMe:
#            if plottable.autoscale:
                w.scaleOnCurve(plottable)  
            if w.isAutoScale():
                w.zoomOutFull()        
            canvas.draw()
            plottable.line.set_label(plottable.name)
        
        if w.firstCurve:
            w.emit(QtCore.SIGNAL("logFlagChangedY"),w.logscaleflag)
            w.emit(QtCore.SIGNAL("logFlagChangedX"),w.logscaleflag_x)
            self.firstCurve = False


plotManager = PlotManager()


