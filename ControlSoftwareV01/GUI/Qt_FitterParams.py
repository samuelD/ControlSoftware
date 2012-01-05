from UI_FitterParams import Ui_FitterWin
from PyQt4 import QtGui,QtCore
import os
from ..core import utils
from numpy import log10
def checkFitDefaultsDir():
    if not os.path.exists(utils.path.getFitDefaultDir()):
		os.mkdir(utils.path.getFitDefaultDir())
checkFitDefaultsDir()
class paramLine(QtCore.QObject):
    def __init__(self,parentWin,name = "newParam",bounds = None):
        QtCore.QObject.__init__(self)
        self.name = name
        self.parentWin = parentWin
        self.nPoints = 1000
        self.label = QtGui.QLabel(name,parentWin.gridLayoutWidget)
        parentWin.gridLayout.addWidget(self.label)
        self.fittedVal = QtGui.QLCDNumber(parentWin.gridLayoutWidget)
        self.fittedVal.setNumDigits(7)
        
        
        
        
        parentWin.gridLayout.addWidget(self.fittedVal)
        self.guessVal = QtGui.QDoubleSpinBox(parentWin.gridLayoutWidget)
        self.guessVal.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)
        
        self.guessVal.setMinimum(-1e244)
        self.guessVal.setMaximum(1e244)
        
        parentWin.gridLayout.addWidget(self.guessVal)
        self.slider = QtGui.QSlider(parentWin.gridLayoutWidget)
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.slider.setMinimumWidth(100)
        parentWin.gridLayout.addWidget(self.slider)
        
        
        self.buttonGroup = QtGui.QButtonGroup()
        self.fixed = QtGui.QRadioButton()
        self.buttonGroup.addButton(self.fixed)
        parentWin.gridLayout.addWidget(self.fixed)
        self.free  = QtGui.QRadioButton()
        self.buttonGroup.addButton(self.free)
        parentWin.gridLayout.addWidget(self.free)
        self.guessThis = QtGui.QRadioButton()
        self.buttonGroup.addButton(self.guessThis)
        parentWin.gridLayout.addWidget(self.guessThis)
        
        self.guessThis.setChecked(True)
        
        
        self.setLast = QtGui.QCheckBox(parentWin.gridLayoutWidget)
        parentWin.gridLayout.addWidget(self.setLast)
        
        self.buttonChangeBounds = QtGui.QPushButton(parentWin.gridLayoutWidget)
        self.buttonChangeBounds.setText("changeBounds")
        parentWin.gridLayout.addWidget(self.buttonChangeBounds)
        
        utils.misc.setToNoDefault(self.buttonChangeBounds)
        
        self.slider.sliderMoved.connect(self.slideMoved)
        self.guessVal.editingFinished.connect(self.editingFinished)
        self.buttonChangeBounds.clicked.connect(self.changeBounds)
        
        self.connect(self,QtCore.SIGNAL("plotGuess"),self.parentWin.plotCurrentGuess)
        self.connect(self,QtCore.SIGNAL("save"),self.parentWin.save)
        self.slider.sliderReleased.connect(self.parentWin.plotCurrentGuess)
        self.slider.sliderReleased.connect(self.emitSave)#### not satisfying didn't find better yet
        self.guessThis.clicked.connect(self.emitSave)
        self.fixed.clicked.connect(self.emitSave)
        self.free.clicked.connect(self.emitSave)
        self.setLast.clicked.connect(self.emitSave)
        
        
        if bounds == None:
        	bounds = [-300,300]
        self.setBounds(bounds)
        
        
    def emitSave(self):
        self.emit(QtCore.SIGNAL("save"))    
        
    def getConstraintStr(self):
        if self.isFixed():
            return "fixed"
        if self.isFree():
            return "free"
        return "toGuess"
    
    def isUseLast(self):
        return self.setLast.isChecked()
    
    def save(self,f):
        import ConfigParser
        cp = ConfigParser.ConfigParser()
        d = dict()
        b = self.getBounds()
        d["min"] = b[0]
        d["max"] = b[1]
        d["guess"] = self.getGuessVal()
        d["constraint"] = self.getConstraintStr()
        d["useLast"] = self.isUseLast()
        utils.dict_CP.saveDictToConfParser(d,cp,self.name)
        cp.write(f)
                
        
    def isFixed(self):
        return self.fixed.isChecked()
    
    def isGuess(self):
        return self.guessThis.isChecked()
    
    def isFree(self):
        return self.free.isChecked()
    
    def setFixed(self):
		self.fixed.setChecked(True)
        
    def setGuessThis(self):
        self.guessThis.setChecked(True)
        
    def setFree(self):
        print "check free" + self.name
        self.free.setChecked(True)
        
    def changeBounds(self):
		print "press enter"
		min = float(raw_input("enter new lower bound"))
		max = float(raw_input("enter new higher bound"))
		self.setBounds([min,max])
		self.emit(QtCore.SIGNAL("save"))
	
		
    def setBounds(self,bounds):	
        self.guessVal.setDecimals(int(4-log10(bounds[1]-bounds[0])))
        self.bounds = bounds
        self.scale = self.nPoints/(bounds[1]-bounds[0])
        self.slider.setMinimum(bounds[0]*self.scale)
        self.slider.setMaximum(bounds[1]*self.scale)
        #self.guessVal.setMinimum(bounds[0])
       # self.guessVal.setMaximum(bounds[1])
    def getBounds(self):
		return self.bounds
	
    def load(self,cp):
        """load from a configParser"""
        d = utils.dict_CP.configParserToDict(cp,self.name)
        
        self.setBounds([d["min"],d["max"]])
        if d["constraint"] == "fixed":
            self.setFixed()
        if d["constraint"] == "free":
            self.setFree()
        if d["constraint"] == "toGuess":
            self.setGuessThis() 
        self.setUseLast(d["uselast"])
        self.setGuessVal(d["guess"])
        
        
    def setUseLast(self,bool):
        self.setLast.setChecked(bool)
    
    def editingFinished(self):
        val = self.guessVal.value()
        self.slider.setValue(val*self.scale)
        self.emit(QtCore.SIGNAL("plotGuess"))
        self.emit(QtCore.SIGNAL("save"))
      #  self.set(val)
        
        
    def slideMoved(self,val):
        val = val/self.scale
        self.guessVal.blockSignals(True)
        self.guessVal.setValue(val)
        self.guessVal.blockSignals(False)
        #self.emit(QtCore.SIGNAL("plotGuess"))
	        #self.set(val)
    def setFittedVal(self,val):
		self.fittedVal.display(val)
		if self.setLast.isChecked():
			self.setGuessVal(val)
	
    def setGuessVal(self,val):
        self.guessVal.setValue(val)
        val = max(val,self.bounds[0])
        val = min(val,self.bounds[1])
        if val == val:
            self.slider.setValue(val*self.scale)
	
    def getGuessVal(self):
		return self.guessVal.value()
		
class Qt_FitterParams(QtGui.QDialog, Ui_FitterWin):
    def __init__(self, fitter,parent = None):
        # self.nFields = nMax
        self.name = fitter.ID_STR
        super(Qt_FitterParams, self).__init__(parent)
        self.setupUi(self)
        import os
        self.current = None
        self.setWindowIcon(QtGui.QIcon(os.path.join(utils.path.getIconDir(),"number6.png")))
        self.paramLines = []
        self.setWindowTitle("fit parameters for " + self.name)
        self.isPlotGuess = False
        self.button_plot_guess.stateChanged.connect(self.togglePlotGuess)
        self.buttonFit.clicked.connect(self.fit)
        self.button_do_guess.clicked.connect(self.doGuess)
        
        utils.misc.setToNoDefault(self.buttonFit)
        utils.misc.setToNoDefault(self.button_do_guess)
        utils.misc.setToNoDefault(self.button_all_fixed)
        utils.misc.setToNoDefault(self.button_all_free)
        utils.misc.setToNoDefault(self.button_all_guess)
        utils.misc.setToNoDefault(self.button_take_all)    
        
        self.connect(self,QtCore.SIGNAL("plotGuess"),self.plotCurrentGuess)
        
        self.offset = 70
        self.lineHeight = 35
        self.width = 750
		
        for i in fitter.PARAMS:
            self.addParam(i)
        self.load()
    
        
        self.button_take_all.setText("all on")
        self.button_all_fixed.clicked.connect(self.all_fixed)
        self.button_all_free.clicked.connect(self.all_free)
        self.button_all_guess.clicked.connect(self.all_to_guess)
        self.button_take_all.clicked.connect(self.all_use_last)
        
    def fitFailled(self):
        self.setStatus(False)
        
    def isStopped(self):
        if self.radioButton_stopAnyWay.isChecked():
            return True
        if self.radioButton_stopIfError.isChecked():
            return self.label_error.text() == "BAD"
        if self.radioButton_noInterrupt.isChecked():
            return False
    
    def setStatus(self,bool):
        if bool:
            self.label_error.setText("OK")
 #           self.label_error.setColor(QtGui.QColor("green"))
        else:
            self.label_error.setText("BAD")
#            self.label_error.setColor(QtGui.QColor("red"))
    
    def doGuess(self):
        self.emit(QtCore.SIGNAL("plotGuess"))
        self.current.doGuess()
    
    def all_use_last(self):
        t = self.button_take_all.text()
        if t=="all on":
            new = True
            self.button_take_all.setText("all off")
        else:
            new = False
            self.button_take_all.setText("all on")
        for i in self.paramLines:
            i.setUseLast(new)
        self.save()
    def all_fixed(self):
        for i in self.paramLines:
            i.setFixed()
        self.save()
    def all_free(self):
        for i in self.paramLines:
            i.setFree()
        self.save()
    def all_to_guess(self):
        for i in self.paramLines:
            i.setGuessThis()
        self.save()
    
    def fit(self):
        self.current.fit()
        self.current.plot() 
        
    def plotCurrentGuess(self):
        if self.isPlotGuess:
            self.current.plotGuess()    
    
    def addParam(self,parName,bounds = [-100.0,100.0]):
        self.paramLines.append(paramLine(self,parName,bounds = bounds))
        self.resize(self.width,self.offset + self.lineHeight*len(self.paramLines))
	
    def setFitterAsCurrent(self,fitter):
        if self.current is not None:
            self.current.parentCurve.setHighlighted(False)
        self.current = fitter
        self.label_current.setText(fitter.parentCurve.name)
        self.current.parentCurve.setHighlighted(True)
        try:
            self.updateFittedValues(fitter.param_fitted)
        except AttributeError:
            pass
        fitter._usePanel_ = True
    def is_guess_required(self):
        for i in self.paramLines:
            if not i.isGuess():
                return True
        return False
    
    def getLineFromName(self,name):
		for i in self.paramLines:
			if i.name == name:
				return i
    def setFittedVal(self,name,val):
		self.getLineFromName(name).setFittedVal(val)
		
    def setGuessVal(self,name,val):
		self.getLineFromName(name).setGuessVal(val)
				
    def getGuessVal(self,name):
		return self.getLineFromName(name).getGuessVal()
				
    def setBounds(self,name,bounds):	
		self.getLineFromName(name).setBounds(bounds)
		self.emit(QtCore.SIGNAL("save"))
		
    def updateFittedValues(self,paramFitted):
		for i in paramFitted:
			self.setFittedVal(i,paramFitted[i])
		
    def getFileName(self):
		return os.path.join(utils.path.getFitDefaultDir(),self.name + ".cfg")

    def togglePlotGuess(self):
        self.isPlotGuess = not self.isPlotGuess
        if self.isPlotGuess:
            self.emit(QtCore.SIGNAL("plotGuess"))
        
    def save(self):
        with open(self.getFileName(),"w") as f:
            for i in self.paramLines:
                i.save(f)
            
            
                
        
    def setParamGuess(self,newPar):
		for i in newPar:
			self.setGuessVal(i,newPar[i])
 
    def paramFreeChanged(self,newPar):
        self.setParamGuess(newPar)
        for i in newPar:
            self.setFree(i)
    
    def paramToGuessChanged(self,newPar):
        self.setParamGuess(newPar)
        for i in newPar:
            self.setGuessThis(i)
    
    def setGuessThis(self,parName):
        self.getLineFromName(parName).setGuessThis()
               
    def setFree(self,parName):
        self.getLineFromName(parName).setFree()           
               
    def unGuess(self,parName):
        """sets the parameter to free if it was on guess this"""
        if self.isGuess(parName):
            self.setFree(parName)
               
    def paramFixedChanged(self,newPar):
        self.setParamGuess(newPar)
        for i in newPar:
            self.setFixed(i)

    def setFixed(self,name):
        self.getLineFromName(name).setFixed()
    
    def getFixedParams(self):
        d = dict()
        for i in self.paramLines:
            if i.isFixed():
                d[i.name] = i.getGuessVal()
        return d
    
#    def isAutoguess(self):
 #       return self.check_autoguess.isChecked()
    def getFreeParams(self):
        d = dict()
        for i in self.paramLines:
            if i.isFree():
                d[i.name] = i.getGuessVal()
        return d
    
    def getToGuessParams(self):
        d = dict()
        for i in self.paramLines:
            if i.isGuess():
                d[i.name] = i.getGuessVal()
        return d
    
    def getGuessParams(self):
#        if self.isAutoguess():
#            return None
        d = dict()
        for i in self.paramLines:
                d[i.name] = i.getGuessVal()
        return d
    
    def isFixed(self,parName):
        return self.getLineFromName(parName).isFixed()
        
        
    def isGuess(self,parName):
        return self.getLineFromName(parName).isGuess()
    
    def load(self):
        if not os.path.exists(self.getFileName()):
            return
        import ConfigParser
        with open(self.getFileName()) as f:
            cp = ConfigParser.ConfigParser()
            cp.readfp(f)
        for i in self.paramLines:
            from ConfigParser import NoSectionError
            try:
                i.load(cp)
            except NoSectionError:
                print "no infos about param %s found for fitter %s"%(i.name,self.name)
    def waitForOK(self):
        if self.radioButton_noInterrupt.isChecked():
            return
        from .. import app
        while(self.radioButton_stopAnyWay.isChecked()):
            app.processEvents()