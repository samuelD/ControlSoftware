### This file simply defines the decorator used to create sessions from a function since version 7 (replaces the very heavy Session.py)

### The new philosophy is that a session is simply defined by the definition of a function, preceded by the decorator @session...
### The session is then launched inline in Ipython, all the kwds of the function with the correct type (string, bool, int, float) are automatically 
### swallowed by the dynamic variable GUI and saved for subsequent use of the session (of course a specified kwd overwrites the GUI value...) 

import utils,os
from collections import OrderedDict

sourceDir = utils.path.getSourceDir()
sessionDir = os.path.join(sourceDir,"sessions")

import loadSave
from PyQt4 import QtCore
from PyQt4.QtCore import QObject

#from ..GUI import Qt_dynamicVariables
from flags import DVGui
    
 
    
class SessionGUIsynchronizer(QObject):
    def __init__(self):
        QObject.__init__(self)
    
    def saveKwds(self,allKwds):
        """takes all the function kwds (as present in the definition), and creates the corresponding slots in the GUI"""
        pass
        
    def updateGUI(self,kwds):
        """ """
        pass
    
    
    
class myParam:
    def __init__(self,ses,name,val = "?",type = None):
        self.val = val
        self.ses = ses
        self.name = name
        
        if type is not None:
            self.type = type
        else:
            self.type = getType(val)
        self.callback = None
        
    def __str__(self):
        if self.type == "?":
            return "?"
        return str(self.val)
    
    def knownType(self):
        return self.type != "?"
    
    def setValue(self,val):
        self.val = val
        self.type = getType(val)
        self.ses.setLiveParamValue(self.name,self.val)
    
    def getGUIObject(self):
        return DVGui.getField(self.name)
    
    def getValue(self):
        val = self.getGUIObject().value()
        self.setValue(utils.dict_CP.convertSmartly(str(val)))
        return self.val
    
def getKwdsKeys(fn):
    pass
    
def getType(val):
    if(val == "?"):
        return "?"
    if isinstance(val,bool):
        return "bool"
    if isinstance(val,int):
        return "int"
    if isinstance(val,float):
        return "double"
    if isinstance(val,basestring):
        return "string"
    return "?"

def getSessionFileName(funcName):
    return os.path.join(sourceDir,"conf","defaultSessions",funcName + ".ses")

def skipFuncCode(f):
    a = f.readline()
    while(a != "[END_CODE]\n"):
        a = f.readline()
        if a=="":
            return

def funcName(func):
        return func.__name__

#def getKwdsDef(func):
#    """return a configParser in which the keys are all new, but doesn't overwrite the corresponding values from the file"""
    
    
status =  "N/A"
activeSession = None
      
class SessionStoppedError(Exception):
    def __init__(self,*args,**kwds):
        Exception.__init__(self,*args,**kwds)
        
      
def listen():
    global status
    if status == "RUNNING":
        return
    if status =="N/A":
        return
    if status == "STOPPING":
        raise SessionStoppedError("session was stopped by user")
    if status == "PAUSING":
        DVGui.setStatus("PAUSED")
    while status == "PAUSED" :
        from flags import app
        app.processEvents()
    if status == "WAITTING DEBUG":
        DVGui.setStatus("DEBUG")
        import pdb
        pdb.set_trace()
        DVGui.setStatus("RUNNING")
    
    
    return listen()
        
def changeSignature(newFunc,func):
    """not sure what this should do, to be tested, at least pass the docstring, maybe more"""
    pass
        
        

        
def setParams(param):
    print param


######################################################
### was copied from positionLogger in Qt_plot.py, needs to be unified e.g in utils.py
class sessionLogger(QtCore.QTimer):
    ARMED = 1
    IDLE  = 0
    def __init__(self,ses):
        QtCore.QTimer.__init__(self)
        self.state = self.IDLE
        self.ses = ses
        self.timeout.connect(self.disArm)
    
    def arm(self):
        if self.state == self.IDLE:
           self.state = self.ARMED
           self.start(1000)
           
                    
    def disArm(self):
        self.stop()
        self.state = self.IDLE
        self.ses.save()

class newSession(QtCore.QObject):
    def __init__(self,func):
        QtCore.QObject.__init__(self)
        self.connect(self,QtCore.SIGNAL("showDVs"),DVGui.showDVs)
        self.func = func
        self.params = self.encapsulateParams(self.paramsFromSignature())
        self.name = func.__name__    
        self.saveTimer = sessionLogger(self)
    
    def getParamVal(self,name):
        return self.params[name].val
    
    def addLiveParams(self):
        """adds global variables accessible in the function to easily get the value of the parameters"""
        #import functools
        for k,v in self.params.iteritems():
            if v.knownType():
                self.func.func_globals[k] = self.getParamVal(k)
                            
    def reformatKwd(self,kwd):
        return "_" + kwd       
          
    def reformatKwds(self,kwds):
        newK = []
        newV = []
        for (k,v) in kwds.iteritems():
            if k in self.params:
                newK.append(self.reformatKwd(k))
            else:
                newK.append(k)
            newV.append(v)
        return OrderedDict(zip(newK,newV))
    
                       
    def __call__(self,directory = "__default__",*args,**kwds):
        self.updateParamsCompatibleTypes(self.paramsFromFile())
        self.updateParams(kwds)
        kwds = self.updateNonDestructively(kwds)
        self.save()
        self.showParams()
        if status != "WAITTING DEBUG":
            self.setStatus("RUNNING")
            
        self.addLiveParams()
        def newFunc(*args,**kwds):
            try:
                self.func(*args,**self.reformatKwds(kwds))
            except SessionStoppedError:
                print """session stopped by user,
catch the SessionStoppedError in the session to perform saving or clean-ups..."""
        async_func = utils.misc.async(newFunc)
        
        if directory == "__default__":
            directory = self.name
        from .. import DVGui
        if DVGui.checkBox.isChecked():
            loadSave.newSessionDir(directory)
        ret = async_func(*args,**kwds)
        self.setStatus("N/A")
        return ret
    
    def setLiveParamValue(self,name,val):
        self.func.func_globals[name] = val
        
    def setStatus(self,status):
        DVGui.setStatus(status)
        global activeSession
        if status == "N/A":
            return
        activeSession = self
       
#    def dumpParamsAsGlobals(self):
#        for k,v in self.params:
#            if v.knownType():
#                self.__call__.func_globals["k"] = v.val   
        
    def updateNonDestructively(self,kwds):   
        for k,v in self.params.iteritems():
            try:
                kwds[k]
            except KeyError:
                if v.knownType():
                    kwds[k] = v.val
        return kwds
               
    def paramsFromFile(self):
        """returns an ordered dictionnary containing the parameters as stored in the file of the session"""
        import ConfigParser
        cp = ConfigParser.ConfigParser()
        try:
            with open(getSessionFileName(self.name)) as f:
                skipFuncCode(f)
                cp.readfp(f)
        except IOError:
            return OrderedDict()
        try:
            ret =  utils.dict_CP.configParserToDict(cp, "KWDS")
        except ConfigParser.NoSectionError:
            return OrderedDict()
        return ret

    def argMatch(self,argName):
        if argName[0] == "_":
            return True
        return False
    
    def argNewName(self,oldName):
        return oldName[1:]
    
    
    def paramsFromSignature(self):
        """from the definition of a function, returns the list of kwd names (in the correct order) in an OrderedDict"""
        fn = self.func
        code = fn.func_code
        argcount = code.co_argcount
        argnames = code.co_varnames[:argcount]
        fn_defaults = fn.func_defaults or list()
        z = zip(argnames[-len(fn_defaults):],fn_defaults)
        newName = []
        newVal = []
        for (n,v) in z:
            if self.argMatch(n):
                newName.append(self.argNewName(n))
                newVal.append(v)
        o = OrderedDict(zip(newName,newVal))
                
        return o
        
    def updateParamsCompatibleTypes(self,paramsFile):
        paramsFile = self.encapsulateParams(paramsFile)
        for p in self.params:
            try:
                file = paramsFile[p]
            except KeyError:
                pass
            else:
                sig = self.params[p]
                if sig.knownType() and sig.type == file.type:
                    self.params[p] = file
    
    def updateParams(self,kwds):
        newParams = self.encapsulateParams(kwds)
        for pSig in self.params:
            try:
                newVal = newParams[pSig]
            except KeyError:
                pass
            else:
                self.params[pSig] = newVal
    
    def saveLater(self):
        self.saveTimer.arm()
    
    
#    def _updateSignature_(self):
#        self.
    
    def save(self):
        """saves func in the corresponding file with its source code and the params as transmitted in func.params (ordered dict)"""      
        import ConfigParser
        #self._updateSignature_()
        
        cp = ConfigParser.ConfigParser()
        cp.add_section("KWDS")
        for k,v in self.params.iteritems():
            cp.set("KWDS",k,str(v))    
    
        with open(getSessionFileName(self.name),"w") as f:
            f.write("[CODE]\n the code should be here\n[END_CODE]\n")
            cp.write(f)
    
    
    def encapsulateParams(self,kwds):
        d = OrderedDict()
        for k,v in kwds.iteritems():
            d[k] = myParam(self,k,v)
        return d

    def showParams(self):
        """displays the parameters in the GUI"""
        self.emit(QtCore.SIGNAL("showDVs"),self.params)
            

### definition of the function used as a decorator (this function takes the provided func as arguments, and returns a enriched version of it)
def session(func):
    """this gets executed once, when the function definition is read... this is the time to save the requested kwds..."""
    ns = newSession(func)
    import functools
    ns = functools.update_wrapper(ns,func)
    paramsFile = ns.paramsFromFile() 
    ns.updateParamsCompatibleTypes(paramsFile)
    ns.save()

    return ns