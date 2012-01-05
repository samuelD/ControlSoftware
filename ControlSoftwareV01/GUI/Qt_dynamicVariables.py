from UI_dynamicVariables import Ui_Dialog
from PyQt4 import QtGui,QtCore

from ..core import newSession
from ..core import utils
from ..core import loadSave
import os



class MyDoubleSpinBox(QtGui.QDoubleSpinBox):
    def __init__(self,win,param):
        QtGui.QDoubleSpinBox.__init__(self,win)
        self.setRange(-1e30,1e30)
        self.param = param
        
    def MyConfig(self,nDecimals = 3):
        self.setDecimals(nDecimals)
        
    def signalChanged(self):
        return self.valueChanged
        
class MySpinBox(QtGui.QSpinBox):
    def __init__(self,win,param):
        QtGui.QSpinBox.__init__(self,win)
        self.param = param
        
    def MyConfig(self):
        self.setRange(0,1000000)
    def signalChanged(self):
        return self.valueChanged
        
class MyCheckBox(QtGui.QCheckBox):
    def __init__(self,win,param):
        QtGui.QSpinBox.__init__(self,win)
        self.param = param
    
    def MyConfig(self):
        pass
    
    def setValue(self,val):
        self.setChecked(val)
        
    def value(self):
        if self.checkState()==2:
            return True
        else:
            return False
    def signalChanged(self):
        return self.stateChanged
        
class MyLineEdit(QtGui.QLineEdit):
    def __init__(self,win,param):
        QtGui.QLineEdit.__init__(self,win)
        self.param = param
    
    def setValue(self,val):
        self.setText(val)    
        
    def value(self):
        return self.text()    
        
    def MyConfig(self):
        pass
    def signalChanged(self):
        return self.textChanged
    
class MyUnknown(QtGui.QLineEdit):
    def __init__(self,win,param):
        QtGui.QLineEdit.__init__(self,win)
        self.setReadOnly(True)
        self.param = param
    
    def setValue(self,val):
        self.setText(val)    
        
    def value(self):
        return self.text()    
        
    def MyConfig(self):
        pass
    
    def signalChanged(self):
        return self.textChanged
    
    
class Separator:
    def __init__(self,win,offset,name):
        #print "separator " + str(offset)
        l = QtGui.QLabel(win)
        l.setGeometry(QtCore.QRect(70, offset, 50, 21))
        l.setText(name)
        l.show()
        self.label = l
        self.line = QtGui.QFrame(win)
        self.line.setGeometry(QtCore.QRect(10,offset, 200, 5))
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.line.show()
        
        self.line1 = QtGui.QFrame(win)
        self.line1.setGeometry(QtCore.QRect(10,offset+21, 200, 5))
        self.line1.setFrameShape(QtGui.QFrame.HLine)
        self.line1.setFrameShadow(QtGui.QFrame.Sunken)
        self.line1.setObjectName("line1")
        self.line1.show()
        
        win.currentOffset = win.heightField + win.currentOffset
        
    def remove(self):
        self.line.deleteLater()
        self.line1.deleteLater()
        self.label.deleteLater()
        
class Button:
    def __init__(self,win,offset,name,func):
        self.but = QtGui.QPushButton(name,win)
        self.but.setGeometry(QtCore.QRect(10,offset, 200, 21))
        self.but.clicked.connect(func)
        win.currentOffset = win.heightField + win.currentOffset
        self.but.show()
        
    def remove(self):
        self.but.deleteLater()
        
    
class Qt_dynamicVariables(QtGui.QDialog, Ui_Dialog):
    def __init__(self, parent = None):
        # self.nFields = nMax
        super(Qt_dynamicVariables, self).__init__(parent)
        
        
        self.setupUi(self)
        self.field = []
        self.label = []
        self.separator = []
        self.button = []
        self.heightField = 30
        self.offset = 180
        self.currentOffset = self.offset
        
        
        
        import os
        from ..core import utils
        #self.setWindowIcon(QtGui.QIcon(os.path.join(utils.path.getIconDir(),"number6.png")))
        
        self.buttonStop.clicked.connect(self.toggleStop)
        self.buttonPause.clicked.connect(self.togglePause)
        self.buttonDebug.clicked.connect(self.debugPressed)
        
        self.connect(self,QtCore.SIGNAL("update"),self._updateStatus_,QtCore.Qt.QueuedConnection)
        
        
        
        self.buttonBrowse.clicked.connect(self.browseSaveDir)
        self.buttonCreate.clicked.connect(self.createDir)
        self.lineSessionName.textEdited.connect(self.sessionDirEdited)
        
        loadSave.theSaver.connect(loadSave.theSaver, QtCore.SIGNAL("newSessionDir"),self.renewSaveStrings)
        loadSave.theSaver.connect(loadSave.theSaver, QtCore.SIGNAL("newSaveDir"),self.renewSaveStrings)
        loadSave.theSaver.connect(loadSave.theSaver, QtCore.SIGNAL("saved"),self.renewLastSaved)

        loadSave.theSaver.emit(QtCore.SIGNAL("newSaveDir"))
        
        self.setWindowIcon(QtGui.QIcon(os.path.join(utils.path.getIconDir(),"blueGear.png")))
        
        
        if not os.path.exists(utils.path.getSessionDir()):#getDefaultSessionDir()):
            os.mkdir(utils.path.getSessionDir())
#        self.initFields(self.nFields)
#       self.setNumVisible(nVisible)


    def createDir(self):
        sesName = str(self.lineSessionName.text())
        loadSave.newSessionDir(sesName)
        
    def sessionDirEdited(self):
        self.buttonCreate.setVisible(True)
        self.anticipateSaveDirString()    
    
    def anticipateSaveDirString(self):
        dir = loadSave.getCurrentDir()
        d = os.path.split(dir)
        if d == "":
            return
        ses = d[1]
        if ses == "":
            ses = "000"
        saveDir = d[0]
        number = int(ses[0:3])
        number = "%03i"%(number+1)
        name = ses[4:]
        #self.lineSessionName.setText(name)
        self.labelSaveDir.setText(saveDir + "/" +number)    
        
    def browseSaveDir(self):
        from .. import plotManager
        d=plotManager.fileDialog
        dir = str(d.getExistingDirectory())
        if dir == "":
            return
        loadSave.changeSaveDir(dir)

    def renewLastSaved(self,filename):
        self.labelLastSaved.setText(filename)

    def renewSaveStrings(self):
        self.buttonCreate.setVisible(False)
        dir = loadSave.getCurrentDir()
        d = os.path.split(dir)
        ses = d[1]
        saveDir = d[0]
        number_ = ses[0:3]
        name = ses[4:]
        self.lineSessionName.setText(name)
        if ses != "":
            self.labelSaveDir.setText(saveDir + "/" + number_)
        else:
            self.buttonCreate.setVisible(True)
            self.anticipateSaveDirString()



    def setStatus(self,newStatus):
        newSession.status = newStatus
        self.emit(QtCore.SIGNAL("update"))        

    def setButtons(self,*args):
        buttons = [self.buttonStop,self.buttonPause,self.buttonDebug,self.labelExplanation]
        for (b,text) in zip(buttons,args):
            b.setText(text)
            try:
                b.setVisible(text!="")
            except AttributeError:
                pass
    def _updateStatus_(self):
        #import newSession
        self.labelStatus.setText(newSession.status)
        pattern = {"RUNNING":("Stop","Pause","Debug","The session is running..."),
                   "WAITTING DEBUG":("Stop","Pause","Debug","you'll be able to debug at next call of listen()"),
                   "DEBUG":("","","","now debugging with pdb (try: (u)p, (d)own, (c)ontinue)"),
                   "STOPPING":("Kill","","Debug","will stop at next call of listen()"),
                   "PAUSED":("Stop","Restart","Debug","Paused..."),
                   "PAUSING":("Stop","Restart","Debug","will pause at next call of listen"),
                   "N/A":("","","Debug","no session currently running")
                   }
        self.setButtons(*pattern[newSession.status])
        
        
    def showDVs(self,params):
        self.eraseAllFields()
        for name,val in params.iteritems():    
            self.addField(name,val)
            
            
    def debugPressed(self):
        self.setStatus("WAITTING DEBUG")

    def toggleStop(self):
        #import newSession,utils
        if(newSession.status == "STOPPING"):
            utils.misc.myThread.terminate()
            self.setStatus("N/A")
            return
        self.setStatus("STOPPING")
        return
        
    def togglePause(self):
        #import newSession
        if(newSession.status == "RUNNING"):
            self.setStatus("PAUSING")
            return
        if(newSession.status == "PAUSING" or newSession.status == "PAUSED"):
            self.setStatus("RUNNING")
            return
        
        
    def eraseAllFields(self):
        if len(self.field)==0:
            return
        for j in self.label:
            j.deleteLater()
        for i in self.field:
            i.deleteLater()
        for i in self.separator:
            i.remove()
        for i in self.button:
            i.remove()
    
        #ToroidImport.app.processEvents()
        self.field = []
        self.label = []
        self.separator = []
        self.button = []
        self.currentOffset = self.offset

        
        



    def addField(self,name,DV):
        #print self.currentOffset
        dictTypes = {"bool":MyCheckBox,"double" : MyDoubleSpinBox,"int" : MySpinBox,"string":MyLineEdit,"?":MyUnknown}
        type = dictTypes[DV.type]
        d = type(self,DV)
        d.setGeometry(QtCore.QRect(10, self.currentOffset, 111, 22))
        d.setObjectName("field%i"%len(self.field))
        self.field.append(d)
        if DV.type == "?":
            self.field[-1].setValue("?")
        else:
            self.field[-1].setValue(DV.val)
        
        try:
            self.field[-1].MyConfig(nDecimals = DV.precision)
        except AttributeError:
            self.field[-1].MyConfig()
        d.show()

        l = QtGui.QLabel(self)
        
        l.setGeometry(QtCore.QRect(130, self.currentOffset, 141, 21))
        self.currentOffset = self.heightField + self.currentOffset
        l.setObjectName("label%i"%len(self.field))
        l.setText(name)
        l.show()
        self.label.append(l)
        #self.nFields = self.nFields + 1
        self.resize(self.width(),self.offset+self.currentOffset)
        
        d.signalChanged().connect(DV.getValue)
        d.signalChanged().connect(DV.ses.saveLater)
            
        if DV.callback is not None:
            d.valueChanged.connect(DV.callback)    
            
    def addSection(self,sectionName):
        self.separator.append(Separator(self,self.currentOffset,sectionName))
        self.resize(self.width(),self.offset+self.currentOffset)
        #self.currentOffset = self.currentOffset + self.heightField 
       
    def addButton(self,name,func):    
        self.button.append(Button(self,self.currentOffset,name,func))
        self.resize(self.width(),self.offset+self.currentOffset)

    def initFromDict(self,d):
        """the dict d can contain name:values e.g.:
        d = {"time":1.23,"freq":70e6,autopilot = True}
        additionally if the corresponding MyConfig function takes argument (e.g. precision for doubles)
        the value can be a tuple containing (value,arg1,arg2,...)
        e.g:d = {"time":(1.23,5),"freq":70e6,autopilot = True}
        """
        lTypes = []
        lNames = []
        lArgs =  []
        lVals =  []
        keys = d.keys()
        keys.sort()
        for i,k in enumerate(keys):
            if isinstance(d[k],tuple):
                val = d[k][0]
                lTypes.append(self.getTypeFromVal(val))
                lArgs.append(d[k][1:])
                lVals.append(val)
            else:
                val = d[k]
                lTypes.append(self.getTypeFromVal(val))
                lArgs.append(None)
                lVals.append(val)
            lNames.append(k)
        self.initFields(types = lTypes)
        
        
        for (i,(name,val,args)) in enumerate(zip(lNames,lVals,lArgs)):
            if args == None:
                args = []
            self.field[i].MyConfig(*args)
            self.label[i].setText(name)
            self.field[i].setValue(val)
            
    def indexFromName(self,name):        
        for i,l in enumerate(self.label):
            if str(l.text()) == name:
                return i
        raise KeyError("no DV has the name %s"%name)
         
    def getField(self,indexOrName):
        if isinstance(indexOrName, basestring):
            index = self.indexFromName(indexOrName)
        else:
            index = indexOrName
        return self.field[index]

    def getVal(self,indexOrName):  
        return self.getField(indexOrName).value()
        
    def getInDict(self):
        d = dict()
        for (n,f) in zip(self.label,self.field):
            d[n.text()] = f.value()
        return d
    
    def setVal(self,indexOrName,val):
        self.getField(indexOrName).setValue(val)

DVGui = Qt_dynamicVariables()
DVGui.show()


def getVal(name):
    return DVGui.getVal(name)

    #def setNumVisible(self,num):
    #    self.numVisible = num
    #    for index in range(self.nFields):
    #        self.field[index].setVisible(index<num)
    #        self.label[index].setVisible(index<num)
            
