import math
import numpy
import pickle
from dict_CP import configParserToDict,convertSmartly
#import cfg3He
import string
import subprocess
import os
#import Spectrum
from scipy import constants,signal
#print "done"
from Unit import *

from PyQt4 import QtCore
from PyQt4.QtCore import QThread
import path

#def ipython_logging():
#    import logging.handlers
#    # setup a logging handler to actually print output to the console
#    console = logging.StreamHandler()
#    console.setFormatter(logging.Formatter(logging.BASIC_FORMAT))
#    console.setLevel(logging.DEBUG)
#    # then setup a handler that buffers the output.  the float('inf')'s suppress automatic flushing.
#    memory = logging.handlers.MemoryHandler(capacity=float('inf'),
#                                            flushLevel=float('inf'),
#                                            target=console)
#    memory.setLevel(logging.DEBUG)
#    logging.root.addHandler(memory)
#    logging.root.setLevel(logging.DEBUG)
#    # tell IPython to flush the buffer every time it prints a prompt.
#    import IPython
#    def flush_log(self, *args, **kwargs):
#        memory.flush()
#        raise IPython.ipapi.TryNext
#    ip = IPython.ipapi.get()
#    ip.set_hook("generate_prompt", flush_log)


class MyThread(QThread):
    def __init__(self):
        QThread.__init__(self)
        self.func = None
        self.args = []
        self.kwds = {}
        self.ret = None

    def run(self):
        self.ret = self.func(*self.args,**self.kwds)


myThread = MyThread()

def async(func):
    def newFunc(*args,**kwds):
        myThread.func = func
        myThread.args = args
        myThread.kwds = kwds
        myThread.start()
        while not myThread.isFinished():
            from ... import app
            app.processEvents()
        return myThread.ret

    newFunc.func_doc = func.__doc__
    return newFunc


def logCalls(func):
    def newFunc(*args,**kwds):
        with open(os.path.join(path.getSourceDir(),"log.txt"),"a") as f:
            f.write("\nentering " + str(func) + "\n\targs = " + str(args) + "\n\tkwds = " + str(kwds))
            res = func(*args,**kwds)
            f.write("\n\t-->exiting successfully")
        return res
    return newFunc

@logCalls
def dummyFunc():
    print "dummyFunc"
    
    
def interpFromPlottable(p,val):
    """returns the Y(val) as defined in the plottable p"""
    for (x,y) in zip(p.X,p.Y):
        if val<x:
            return y

def copyToClipboard(text):
    from ..flags import app
    c = app.clipboard()
    c.setText(text)


def coerce(val,interv):
    if val>interv[1]:
        val = interv[1]
    if val<interv[0]:
        val = interv[0]
    return val


def getnextblockcode(fp):
    """returns the text in file fp up to the end of the python code block (same or larger indentation)"""
    l = fp.readline()
    n_indent = len(l)-len(l.lstrip())
    code = l
    l = fp.readline()
    current = len(l)-len(l.lstrip())
    while n_indent<current or l == "\n":
        code = code + l
        l = fp.readline()
        current = len(l)-len(l.lstrip())
    return code.rstrip("\n")
    
def listFromArgsText(argsText):
    vals = []
    argsText = str(argsText)
    if argsText == "":
        return vals
    args = argsText.split("\n")
    
    for i in args:
        try:
            (name,val) = i.split("=")
        except ValueError:
            val = i
        val = val.strip()
        val = convertSmartly(val)
        vals.append(val)
    return vals
    


def saveDictToIniStr(d):
    st = ""
    for i in d:
        st = st + i + " = " + str(d[i])+"\n"
    return st
        
def saveListToIniStr(l):
    st = ""
    for i in l:
        st = st + str(i) + "\n"
    return st



def distance((x1,y1),(x2,y2)):
    return numpy.sqrt((x1-x2)**2 +(y1-y2)**2)

def setToNoDefault(button):
    button.setDefault(False)
    button.setAutoDefault(False)    
 

def rootPoly2(coeffs,val):
    a = coeffs[0]-val
    b = coeffs[1]
    c = coeffs[2]
    delta = b**2-4*a*c
    return (-b-numpy.sqrt(delta))/(2*a)

def _split_tkstring(text):    
    while text:
        part, sep, text = text.partition(u' ')
        if part.startswith(u'{'):
            if part.endswith(u'}'):
                yield part.lstrip(u'{').rstrip(u'}')
            else:
                rest, sep, text = text.partition(u'}')
                yield part.lstrip(u'{') + u' ' + rest
                text = text[1:] #space
        else:
            yield part



def cureBugUnicode(result):
    #BUG in python http://bugs.python.org/issue5712
    if isinstance(result, unicode):
        result = tuple(_split_tkstring(result))
    return result


def nmToMHz(X_nm):
    """converts a wavelength in nm to an arbitrary detuning in MHz"""
    return (constants.c/X_nm - constants.c/X_nm[0])*1000

def dBmToVolts(col):
    """converts the value(s) in col from dBm to Volts"""
    return numpy.exp(math.log(10)*col/10)


#def runArbitraryFunction(func,**args):
#    """runs in a separate python script the function func
#    the function should be picklable/unpickleables, and for the moment, the parameters should be entered as a dictionnary
#    """
#    process = subprocess.Popen("python " + "\"" + os.path.join(cfg3He.installPath,"runArbitraryFunction.py") + "\"", shell = True, stdout = subprocess.PIPE,stdin = subprocess.PIPE)#


#    pickle.dump((func,args),process.stdin)
#    com = process.communicate()[0]
#    return pickle.loads(com)



def smoothenVtoFreq(val1,val2):
    """takes 2 curves from a scope with the second one being the wavelength output of the laser return the 2 curves truncated on the usable part and smoothen the wavelength curve"""
    (b,a) = signal.butter(2,0.00005,btype = "low") # second order low pass filter for X...
    freqFilter = signal.lfilter(b,a,val2)
    

    val2inv = val2[::-1]
    freqFilterInv =  signal.lfilter(b,a,val2inv)

    freqFilter = (freqFilter + freqFilterInv[::-1])/2

    freqFilter = VtoFreq(freqFilter) + 0.05 ## it shoudn t be, but who knows
    
    margin = 100000
    
    return (val1[margin:-margin],freqFilter[margin:-margin])


def smoothenVtoFreqOld(val1,val2):
    """takes 2 curves from a scope with the second one being the wavelength output of the laser return the 2 curves truncated on the usable part and smoothen the wavelength curve"""    
    nFilterX = 500
    nSmoothX = 50
    freq = []
    freqFilterTemp = []
    for i,j in  enumerate(range(0,len(val2),nFilterX)):
        freq.append(val2[j:j+nFilterX].mean())
    freq = numpy.array(freq)
    for i,j in enumerate(freq):
        freqFilterTemp.append(VtoFreq(freq[i:i+nSmoothX].mean()))
    freqFilterTemp = numpy.array(freqFilterTemp)
          
          
    freqFilter = []#numpy.zeros(nSmoothX*nFilterX/2).tolist()
    for i,j in enumerate(freqFilterTemp):
        if i+1 >= len(freqFilterTemp):
            break
        freqFilter.extend(numpy.linspace(j,freqFilterTemp[i+1],nFilterX,endpoint = False))
    freqFilter = numpy.array(freqFilter)
  

    delayFilter = nSmoothX*nFilterX/2
    return (val1[delayFilter:],freqFilter[:len(val1)-delayFilter])


def transferKeyValuePair(src,dest,key):
    try:
        val = src.pop(key)
    except KeyError:
        return None
    dest[key] = val

class radioButtonGroup:
    """a mutually exclusive group of 3 radiobuttons"""
    def __init__(self,*args):
        """args should be in the form (button1,callbackFunction1),(button2,callbackFunction2)..."""
        self.button = []
        for (b,c) in args:
            self.button.append(b)
            b.clicked.connect(c)
        self.set(0)
        

    def set(self,nr):
        for i,b in enumerate(self.button):
            b.setChecked(i==nr)

    def get(self):
        for i,b in enumerate(self.button):
            if b.isChecked():
                return i


def VtoFreq(volt):
    return (volt - 0.128977)/(8.289058-0.128977)*(781.67-764.64)+764.64
    

######## 0.128977 V for 764,64nm
######## 8.289058 V for 781.67nm
    


def loadDummyCurve():
    from .. import Spectrum
    val1 = pickle.load(open("x:\\physicsKlab\\He3\\He3Control\\val1.dat"))#"/home/samuel/physicsKlab/He3/He3Control/val1.dat"))#
    val2 = pickle.load(open("x:\\physicsKlab\\He3\\He3Control\\val2.dat"))#"/home/samuel/physicsKlab/He3/He3Control/val2.dat"))#"c://He3Control//val2.dat"))
    sp = Spectrum.speOpt()
    (sp.Y,sp.X) = smoothenVtoFreq(val1,val2)
    return sp






class multiConfig:
    """a class supposed to store multiple possible configurations into a log file (e.g. for shutters, na states...)"""
    def __init__(self,name = ""):
        self.name = name
        self.path = os.path.join(path.getConfDir(),name + ".conf") 
        self.states = [] #the dictionnaries containing the necessary infos
        self.names  = [] #a list of names
        if os.path.exists(self.path):
            self.load()
        
    def load(self):
        import ConfigParser
        self.states = []
        self.names = []
        c = ConfigParser.ConfigParser()
        c.read(self.path)
        sec = c.sections()
        sec.sort()
        for s in sec:
            self.states.append(configParserToDict(c, s))
        
    def save(self):
        import ConfigParser
        import dict_CP
        c = ConfigParser.ConfigParser()
        for i,state in enumerate(self.states):
            dict_CP.saveDictToConfParser(state,c,"state%i"%i)
        with open(self.path,"w") as f:
            c.write(f)
    
    def numFromName(self,name):
        for i,s in enumerate(self.states):
            if s["name"] == name:
                return i
        return -1
    
    def addState(self,name,stateDict = None):
        """adds the state in the config list and returns the number that it has taken in the list (if allready existed, then just replaces the old state)"""
        n = self.numFromName(name)
        if stateDict is None:
            stateDict = dict()
        stateDict["name"] = name
        if n==-1:
            self.states.append(stateDict)
            self.save()
            return len(self.states)-1
        else:    
            self.states[n] = stateDict
            self.save()
            return n 
        
    def removeState(self,name):
        n = self.numFromName(name)
        if n == -1:
            return 
        else:
            self.states.remove(self.states[n])
        self.save()
    
    def getState(self,nameOrNum = -1):
        if isinstance(nameOrNum,basestring):
            n = self.numFromName(nameOrNum)
            if n!=-1:
                return self.states[n]
            else:
                raise ValueError("available states for " + self.name + " are %s"%self.states.keys())
        if nameOrNum == -1:
            return self.promptChoice()
        try:
            num = int(nameOrNum)
            if num >= len(self.states):
                raise ValueError()
        except ValueError:
            raise ValueError("available states for " + self.name + " are indexed from 0 to %i"%(len(self.states)-1))
        d = self.states[num]
        return d
    
    def promptChoice(self):
        seq = [(a,b["name"]) for (a,b) in enumerate(self.states)]
        n = raw_input("available " + self.name + " states are :\n" + str(seq) + "\nenter a number:")
        n = int(n)
#        try:
 #           state = self.states[state]
  #      except KeyError:
   #         print "available states for " + self.name + " are %s"%self.states.keys()
        return self.states[n]
    
def PID(err,errLast,Ilast,gP,gI,gD,dt):
    P = gP*err
    I = Ilast + gI*err*dt
    D = gD*(err-errLast)/dt
    return (P,I,D)


def getRefCellV():
    from ...hardware import daqmx
    try:
        V = daqmx.ao.getLastValue(0)
    except:
        return dict()
    return {"V_refCell":V}

def getGeneralGraphVal():
    import os
    d = dict()
    logPath = "C:\oxford\Global Variables\CurrentValues.txt"
    if not os.path.exists(logPath):
        return d
    with open(logPath) as f:
        l = f.readline()
        while l is not "":
            (name,val) = l.split("=")
            name = name.strip()
            val = val.strip()
            d[name] = convertSmartly(val)
            l = f.readline()
    return d


def do_yn(question,func):
    yn = raw_input(question)
    while (yn!="y") and (yn!="n"):
        yn = raw_input("answer by y or n")
    if yn == "y":
        return func()
    