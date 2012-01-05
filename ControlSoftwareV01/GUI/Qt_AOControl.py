from AOControl import Ui_AoControl
from PyQt4 import QtGui,QtCore
import numpy
try:
    from ..hardware.daqmx import ao
except WindowsError:
    ao = None


class AOmover(QtCore.QThread):
    ARMED = 1
    IDLE  = 0
    def __init__(self,win):
        QtCore.QThread.__init__(self)
        self.win = win
        #self.state = self.IDLE
        #self.timeout.connect(win.move)
        #self.timeout.connect(self.disArm)
    
    def run(self):
        self.win.moveToSetPoint()
#    def arm(self):
 #       if self.state == self.IDLE:
  #         self.state = self.ARMED
   #        self.start(30)
                    
 #   def disArm(self):
 #       self.stop()
 #       self.state = self.IDLE

class Qt_AOControl(QtGui.QMainWindow, Ui_AoControl):
    def __init__(self, min = 0,max = 10,setPoint = 0,slewRate = 0.5,parent = None):
        super(Qt_AOControl, self).__init__(parent)
        self.setupUi(self)
        self.buttonLeft.pressed.connect(self.left)
        self.buttonRight.pressed.connect(self.right)
        self.leftSlow.pressed.connect(self.leftSlowly)
        self.rightSlow.pressed.connect(self.rightSlowly)
        self.resolution = 10000.0
        self.scale = self.resolution/(max-min)
        self.min = min
        self.max = max
        self.slide.setMinimum(min*self.scale)
        self.slide.setMaximum(max*self.scale)
        self.setPoint.setMinimum(min)
        self.setPoint.setMaximum(max)
        self.moving = False
        self.setPoint.editingFinished.connect(self.setPointEdited)
        self.slide.sliderMoved.connect(self.slideMoved)
        self.connect(self, QtCore.SIGNAL("currentChanged"), self.updateCurrent,QtCore.Qt.BlockingQueuedConnection)
        self.connect(self, QtCore.SIGNAL("currentChanged"),self.moveLeftRight,QtCore.Qt.BlockingQueuedConnection)
        self.connect(self, QtCore.SIGNAL("setPointChanged"),self.setGUIsetPoint)
        self.connect(self, QtCore.SIGNAL("setCheckboxSlowly"),self.checkBox.setChecked)
        #self.timerRight.timeout.connect(self.right)
        #self.timerLeft.timeout.connect(self.left)
#        self.treeWidget.itemChanged.connect(self.itemChanged)
    
 #       self.setWindowIcon(QtGui.QIcon(os.path.join(utils.getIconDir(),"checkbox_icon2.gif")))
        self.step = 0.1
        self.slowStep = 0.001
        self.mover = AOmover(self)
        self.sp = 5
        self.cur = 5
        self.stepTime = 100 #ms
        self.slewRate.setValue(slewRate)
        self.checkBox.setCheckState(True)
        self.cur = setPoint
        self.setSlideBarValue(setPoint)
        self.updateCurrent(setPoint)
        #self.setV(setPoint)
        
#    def coucou(self,event):
 #       1/0
  #      print "coucou"
  
    def moveLeftRight(self):
        if self.buttonRight.isDown():
            self.right()
        if self.buttonLeft.isDown():
            self.left()
            
        if self.rightSlow.isDown():
            self.right(slow = True)
        if self.leftSlow.isDown():
            self.left(slow = True)
    def setPointEdited(self):
        val = self.setPoint.value()
        self.slide.setValue(val*self.scale)
        self.set(val)
  
    def slideMoved(self,val):
        val = val/self.scale
        self.setPoint.blockSignals(True)
        self.setPoint.setValue(val)
        self.setPoint.blockSignals(False)
        self.set(val)
        #print "slideMoved"
    
    def leftSlowly(self):
        self.left(slow = True)
        
    def rightSlowly(self):
        self.right(slow = True)
        
    def left(self,slow = False):
  #      self.set(self.get()-self.step)
        step = {True:self.slowStep,False:self.step}[slow]
        val = max(self.get()-step,self.min)
        self.setPoint.setValue(val)
        self.slide.setValue(val*self.scale)
        self.set(val)
        
        
    def right(self,slow = False):
 #       self.set(self.get()+self.step)
  #      self.slide.setValue(self.get())
        #self.timerRight.start(self.stepTime)
        step = {True:self.slowStep,False:self.step}[slow]
        val = min(self.get()+step,self.max)
        self.setPoint.setValue(val)
        self.slide.setValue(val*self.scale)
        self.set(val)
        
    def setMoving(self,bool):
        self.moving = bool    
        if bool:
            self.mover.start()
#        else:
 #           self.mover.disArm()
        
    def current(self):
        return self.cur    
    
    def setSlideBarValue(self,val):    
        self.slide.setValue(val*self.scale)
        
    def updateCurrent(self,val):
        self.progressBar.setValue(int(val*1.0/(self.max-self.min)*100))
        self.currentPoint.display(val)
                                  
    def moveCurrent(self,val):
        self.cur = val
        if ao!=None:
            ao.setCh(0,val,slowly = self.checkBox.isChecked(),slewRate = self.slewRate.value())
        else:
            import time
            time.sleep(0.1)
            print "No ao board detected, I am just pretending that it is there..."
        self.emit(QtCore.SIGNAL("currentChanged"),val)
          
    
    def moveToSetPoint(self):
        """the function tries to get closer to the setPoint and disarm the timer if it arrives"""    
        delta = self.get()-self.current()
        newV = self.current()
        while(delta!=0):
            if abs(delta)<self.step:
                newV = self.get()
                self.setMoving(False)
            else:
                newV =self.current()+ numpy.sign(delta)*self.step
            #print "moving laser to " + str(newV)
            self.moveCurrent(newV)
            delta = self.get()-self.current()       
            
            
    def get(self):
        return self.sp
    
    def set(self,val):
        #print val
        #print self.cur
        if val == self.sp:
            return
        #self.slide.setValue(val)
        self.sp = val
        self.setMoving(True)
        
    def scan(self,Vmin,Vmax,n = 0):
        """performs a scan at the max slew rate"""
        if n == 0:
            n=1000000
        for i in range(n):
            self.setV(Vmin)
            self.setV(Vmax)
            
        
    def setGUIsetPoint(self,V):
        self.slide.setValue(V*self.scale)
        self.setPoint.setValue(V)
        
    def setV(self,V,slowly = None,wait = True):
        """change the voltage of ao channel 0 without bypassing the nice GUI slidebars
        slowly = True/False will change the checkbox value as well
        slowly = None won't"""
        if V >10:
            V = 10
        if V<0:
            V = 0
        if slowly is not None:
            self.emit(QtCore.SIGNAL("setCheckboxSlowly"),slowly)
        self.emit(QtCore.SIGNAL("setPointChanged"),V)
        self.set(V)
        if wait:
            while not self.mover.isFinished():
                from .. import app
                app.processEvents()          