

import csv
#import numpy
import datetime
#import dircache <-- deprecated module do not use!!! (use os.path instead)
import os
#import string
#import tkFileDialog
#import cfg3He
import utils
from utils import readConfig
#import subprocess
#import pickle

#import Spectrum
import ConfigParser

from PyQt4 import QtCore,QtGui
import shutil
#import ToroidAll

_todayDir_ = None
_currentNumber_ = None

def renewTodayDir():
    global _todayDir_
    _todayDir_ = None
    getTodayDir()

def saveSaveDir(path):
    confFileDir = utils.path.getConfDir()
    with open(os.path.join(confFileDir,"path.cfg"), 'w') as f:
        defaultLoadDir = path
        f.write("saveDir = %s\n"%path)
        f.write("defaultLoadDir = %s\n"%defaultLoadDir)
        

def changeSaveDir(newDir):
    global _todayDir_
    global _currentNumber_
    _todayDir_ = newDir
    _currentNumber_ = None
    saveSaveDir(newDir)
    saveSourceCode(path = newDir)
    theSaver.emit(QtCore.SIGNAL("newSaveDir"))

def isNotSource(dir_,files):
    l = []
    for filename in files:
        if os.path.isdir(os.path.join(dir_,filename)):
            if filename == ".svn":
                l.append(filename)
            else:
                continue
        if (filename[-3:] != ".py")and(filename[-3:] != "cfg"):
            l.append(filename)
    return l
       

def saveSourceFile(moduleFile,path = os.path.join(".","source")):
    filename = moduleFile
    if filename[-3:] == "pyc": ##
        filename = filename[:-1]
    shutil.copyfile(filename,os.path.join(path,os.path.split(filename)[1]))



def listSubDirs(dir_):
    return [i for i in os.listdir(dir_) if os.path.isdir(os.path.join(dir_, i))]

def listFiles(dir_):
    return [i for i in os.listdir(dir_) if os.path.isfile(os.path.join(dir_,i))]

class Saver(QtCore.QObject):
    def __init__(self):
        QtCore.QObject.__init__(self)
theSaver = Saver()

def newSessionDir(name = "newSession"):
    todayDir = getTodayDir()
    currentDir = getCurrentDir()
    if currentDir==todayDir:
        newDir = os.path.join(todayDir  , "001"+"_" + name)
    else:
        try:
            num = int(os.path.split(currentDir)[1].split("_")[0])+1
        except ValueError:
            num = 1
        newDir = os.path.join(todayDir , '%03d' %num +"_"+name)
    os.mkdir(newDir)
    global _currentNumber_
    _currentNumber_ = None
    theSaver.emit(QtCore.SIGNAL("newSessionDir"))
    return newDir


def checkForSource():
    todayDir = getTodayDir()
    if os.path.exists(os.path.join(todayDir,"source")):
        return True
    return False

def checkSourceDir(path):
    """returns path if the file are not saved here or path_2 otherwise"""
    if os.path.exists(path):
        return checkSourceDir(path + "_2")
    return path

def saveSourceCode(saveInAutoGenDir = False,path = None):
    if saveInAutoGenDir:
        path = os.path.join(getTodayDir(),"source")
#        try :
#           os.mkdir(path)
#       except OSError:
#           print "source code was allready saved for that day what the hell is going on???!!!(call Samuel!)"
    else:
        path = os.path.join(path,"source")
    path = checkSourceDir(path)
            #yn = raw_input("path %s allready exists, overwrigth the source code in there anyway?(y/N)")
            #if yn in ["y","Y","yes"]:
            #    pass
            #else:
            #    print "source code was not saved"
            #    return
    #from ToroidImport import listModules
    rootdir = utils.path.getSourceDir()
    shutil.copytree(rootdir, path,ignore = isNotSource)
    #for mod in listModules:
        #if saveInAutoGenDir:
        #   saveSourceFile(mod.__file__,path) #save in todayDir/source/
        #   saveSourceFile(mod.__file__,path)





def getTodayDir():
    global _todayDir_
    if _todayDir_ is not None:
        return _todayDir_
    if os.path.exists(readConfig.saveDir())==False:
        yn = "anyStr"
        while (yn != "y") and (yn != "n"):
            yn = str(raw_input("directory " + readConfig.saveDir() + "doesn't exist, create it? (y/n)"))
            if yn == "y":
                os.mkdir(readConfig.saveDir())
            if yn == "n" :
                raise IOError("base save Directory doesn't exist, I cannot save any data!!!")

    todayStr = str(datetime.date.today())

    list_= listSubDirs(readConfig.saveDir())


    todayDir = ""
    for dir_ in list_:
        if dir_.find(todayStr)==0:#found a dir whose name starts with today's date
            todayDir = os.path.join(readConfig.saveDir(),dir_)

    if todayDir == "":
        # no dir matches today's date create a new one
        print "press enter please, I want to say something"
        name = raw_input("Today's data path doesn't exist what name should we give it? (date will be automatically added). reply n if you don't want to  create date dir")
        if name !="n":
            todayDir = os.path.join(readConfig.saveDir() , todayStr +"_"+ name)
            os.mkdir(todayDir)
            saveSourceCode(saveInAutoGenDir = True)
            _todayDir_ = todayDir
        else:
            todayDir = readConfig.saveDir()
    return todayDir

#getTodayDir()

def __findMaxPrefixIn__(list_):
    """returns  the couple (max,"max_somefilename") corresponding to the list of strings given"""
    # list = dircache.listdir(dir)
    if list_ == []:
        list_ = ["dummy"]
    max_ = 0
    currentDir = ""
    for dir_ in list_:
        try:
            number = int(dir_.split("_")[0])
            if (number > max_):
                max_ = number
                currentDir =  dir_
        except ValueError:
            pass

    #  if max==-1:## first session of today
    #     sessionNum = 1
    #    currentDir = ""
    return (max_,currentDir)


def getCurrentDir():
    #### now look for the last startNr directory
#    todayDir = getTodayDir()
    #print "getCurrentDir called"
    global _todayDir_
    global _currentNumber_
    if _todayDir_ == None:
        _todayDir_ =  getTodayDir()
#        return ""
    if _currentNumber_ is None:
        _currentNumber_ = __findMaxPrefixIn__(listSubDirs(_todayDir_))[1]
    #else:
    #   currentNumber = _currentNumber_
    return os.path.join(getTodayDir(),_currentNumber_)


def appendDataToFile(f,data):
    try:
        data[0]          
    except TypeError:    # <-- single value
        #print "single"
        f.write(str(data))
        return
    
    writer = csv.writer(f)
    try:
        data[0][0]      
    except TypeError:     # <-- one-d array
        #print "1d array"
        for val in data:
            writer.writerow([val])
        return
    
    for i,dummy in enumerate(data[0]):   # <-- 2-d array
        #print "2d array"
        line = []
        for val in data:
            line.append(val[i])
        writer.writerow(line)



def saveToFileName(file_,data):
    """save to a file defined by its filename and then closes the file"""
    with open(file_,"w") as f:
        appendDataToFile(f,data)

def saveKeyValuePairToFile(f,key,data):
    """data can be either a single value, a one-d array, or a 2d array (don't see the use for generalization yet...)"""
    f.write(key + "\n")
    appendDataToFile(f,data)

def loadValueFromFile(f,key):
    pass


def getCurrentTraceID():
    currentDir = getCurrentDir()
    return __findMaxPrefixIn__(listFiles(currentDir))[0]
    
def getCurrentTraceName():
    currentDir = getCurrentDir()
    return __findMaxPrefixIn__(listFiles(currentDir)[1])
    

class Saveable(object):
    """allows to save an object containing the fields
    __EXT__   : the extension of the file
    
    measParam : a dictionary
    
    dateHour  : a dictionary

    path      : if empty and not specified, opens a dialog 
   
    name      : if empty and not specified, opens a dialog
    """
    ext = dict()
    

    
    __YEAR__ = "year"
    __MONTH__= "month"
    __DAY__  = "day"
    __HOUR__ = "hour"
    __MINUTE__= "minute"
    __SECOND__ = "second"
    __MICROSECOND__ = "microsecond"

    __DATE_TIME__ = "DATE AND TIME"
    __MEAS_PARAM__ = "MEAS_PARAM"


    #def saveData(self,f):
    #    pass
   
    def __load_data__(self,f):
        pass
    

    def dateStr(self):
        return "%i/%i/%i, %i:%i.%i"%(self.dateTime[Saveable.__YEAR__],self.dateTime[Saveable.__MONTH__],self.dateTime[Saveable.__DAY__],self.dateTime[Saveable.__HOUR__],self.dateTime[Saveable.__MINUTE__],self.dateTime[Saveable.__SECOND__])
    

    def setDateTimeToNow(self):
        try:
            self.dateTime
        except AttributeError:
            self.dateTime = dict()
        d = datetime.datetime.today()
        self.dateTime[Saveable.__YEAR__] = d.year
        self.dateTime[Saveable.__MONTH__] = d.month
        self.dateTime[Saveable.__DAY__] = d.day
        self.dateTime[Saveable.__HOUR__] = d.hour
        self.dateTime[Saveable.__MINUTE__] = d.minute
        self.dateTime[Saveable.__SECOND__] = d.second
        self.dateTime[Saveable.__MICROSECOND__] = d.microsecond
#    def __loadFromCP__(self,cp): #load the fields of the Section PLOTTABLE from the configParser
#        self.dateTime = utils.configParserToDict(cp,Saveable.__DATE_TIME__)
#        self.measParam =  utils.configParserToDict(cp,Saveable.__MEAS_PARAM__)



    def __init__(self,name = "newTrace",path = "",saveCSVcopy = False,saveInAutoGenDir = False,year = None,month= None,day=None,hour = None,minute = None,second = None,microsecond = None,extra = dict(),skipData = False):
        if(year == None):
            self.setDateTimeToNow()
        else:
            self.dateTime = dict()
            self.dateTime[Saveable.__YEAR__] = year
            self.dateTime[Saveable.__MONTH__] = month
            self.dateTime[Saveable.__DAY__] = day
            self.dateTime[Saveable.__HOUR__] = hour
            self.dateTime[Saveable.__MINUTE__] = minute
            self.dateTime[Saveable.__SECOND__] = second
            self.dateTime[Saveable.__MICROSECOND__] = microsecond
        self.measParam = dict()
        self.measParam.update(extra)
        self.name = name
        self.path = path
        self.saveCSVcopy = saveCSVcopy
        self.saveInAutoGenDir = saveInAutoGenDir
           

    def setPathToNextTrace(self):
        self.name = "%03d" %(getCurrentTraceID()+1) + "_" + self.name 
        self.path = getCurrentDir()    


    def save(self,name = "",path = "", saveInAutoGenDir = None):
        if saveInAutoGenDir != None:
            self.saveInAutoGenDir = saveInAutoGenDir
        if self.saveInAutoGenDir:
            self.setPathToNextTrace()

        if path != "":
            self.path = path
        if name != "":
            self.name = name
        
        
        self.dialog = False
        if(self.dialog == False):
            try:
                if self.name == "":
                    self.dialog = True
            except AttributeError:
                self.dialog = True

            try:
                if self.path == "":
                    self.dialog = True
                    self.path = readConfig.analysisPath()
            except AttributeError:
                self.dialog = True 
                self.path = readConfig.analysisPath()

        if self.dialog == True:
            filename = str(QtGui.QFileDialog.getSaveFileName())
            if filename == "":
                print "Attention, no file selected: curve has not been saved!!!"
                return
            sp = os.path.split(filename)
            self.path = sp[0]
            self.name = sp[1]

        

        filename = os.path.join(self.path,self.name)

        if filename[-4:]!="." + self.__EXT__:
            filename = filename + "." + self.__EXT__
        

        if self.__EXT__ != "csv":
        ########## now start the actual saving        
            c=ConfigParser.ConfigParser()
        
            c.add_section(Saveable.__DATE_TIME__) ### stores the date and times at which the trace was taken
            for key in self.dateTime:
                c.set(Saveable.__DATE_TIME__,key,self.dateTime[key])
            c.add_section(Saveable.__MEAS_PARAM__)
            for key in self.measParam:
                c.set(Saveable.__MEAS_PARAM__,key,self.measParam[key])
        

            with open(filename,"w") as f:
                c.write(f)
                self.__save__(f)
                if self.saveInAutoGenDir:
                    os.chmod(f.name,0)
        else:
            with open(filename,"w") as f:
                self.__save__(f)
                if self.saveInAutoGenDir:
                    os.chmod(f.name,0)


        if self.saveCSVcopy: ### then also save a CSV file of the trace
            self.saveCSV(os.path.splitext(f.name)[0] + ".csv") ## this function is usually defined simply in the Plottable object...
            if self.saveInAutoGenDir:
                    os.chmod(f.name,0)
        theSaver.emit(QtCore.SIGNAL("saved"),filename)
        
def getDict(f):
    cp = extractHeader(f)
    mp = dict(cp.items(Saveable.__MEAS_PARAM__))
    cp.remove_section(Saveable.__MEAS_PARAM__)
    cp.remove_section("DATA")
    
    from ConfigParser import NoSectionError
    fitParams = None
    try:
        fitParams = utils.dict_CP.configParserToDict(cp,"FIT_PARAMS")
    except NoSectionError:
        pass
    cp.remove_section("FIT_PARAMS")
    
    
    d = utils.dict_CP.mergeCPtoDict(cp)
    if fitParams is not None:
        d["param_fitted"] = fitParams
    return (d,mp)

def loadFromFile(f,ext,skipData = False,**kwds):
    if ext!="csv":
        (args,mp) = getDict(f)
    else:
        args = dict()
        args["win"] = "CSV files"
        mp = dict()
    args.update(kwds)
    args["file"] = f
    if skipData:
        args["file"] = None
    args["name"] = os.path.splitext(os.path.split(f.name)[1])[0]
    res = Saveable.ext[ext](**args)
    res.measParam = mp
    return res

#def load(path = "",name = ""):
#    """loads any object inheritting of class Saveable"""
#    dialog = False
#    if path == "":
#        path = cfg3He.defaultLoadDir
#        dialog = True
#    if name == "":
#        dialog = True

#    if dialog:
#        filename = runArbitraryFunction(tkFileDialog.askopenfilename,initialdir = path)
#    else:
#        filename = os.path.join(path,name)
    

#    ext = filename[-3:]
#    with open(filename) as f:
#        return Saveable.load(f,ext)

    
#def load(f,ext):
#        #d = Saveable.ext[ext]()


#    if ext != "csv":
#        cp = extractHeader(f)
#        d = Saveable.ext[ext](configParser = cp,file = f)
#            d.__load_data__(f,cp)    
#    else:
#        d = speOld(win = "CSV files",file = f)
#            d.__load_data__(f,None)
#    d.name = os.path.splitext(os.path.split(f.name)[1])[0]  ### the filename without extension
#    return d

    
def extractHeader(f):
    """returns a ConfigParser extracted from the file truncated down to [DATA]"""
    cp = ConfigParser.ConfigParser()
    line = "dummy"
    #s = ""
    
    while(not("[DATA]" in line)and(line!="")):
        line = f.readline()
        if line.find("[") == 0 : ## new section
            stop = line.find("]")
            if stop>0:
                currentSection = line[1:stop]
                cp.add_section(currentSection)
                continue
            else:
                raise IOError("section should be flagged by [...]")
        l = line.split("=")
        if len(l)==2:
            cp.set(currentSection,l[0].strip(),l[1].strip())
        elif len(l)>2 :
            raise IOError("Only one = allowed on each line...")
    return cp



#def loadMult(path = "",names = []):
#    """loads a list of objects inheritting of class Loadable"""
#    dialog = False
#    if path == "":
#        path = cfg3He.defaultLoadDir
#        dialog = True
#    if names == []:
#        dialog = True

#    if dialog:
#       filenames = utils.cureBugUnicode(runArbitraryFunction(tkFileDialog.askopenfilenames,initialdir = path))
#    else:
#        filenames = [os.path.join(path,name) for name in names]
    

#    ret = []
#    for fn in filenames:
#        ext = fn[-3:]
#        with open(fn) as f:
#            ret.append(Saveable.ext[ext].__load__(f))
#    return ret
    
class dummySave(Saveable):
    __EXT__ = "dum"


def load_dirFromStr(st):
    pass

def load_MultFromStr(filenames,**kwds):
    ret = []
    for fn in filenames:
        ext = fn[-3:]
        with open(fn) as f:
            ret.append(loadFromFile(f,ext,**kwds))
    return ret

def load_fileFromStr(st,**kwds):
    ext = st[-3:]
    with open(st) as f:
        return loadFromFile(f,ext,**kwds)
    


def load(st,skipData = False):
    if isinstance(st,basestring):
        import glob
        list_ = glob.glob(st)
        if len(list_)>1:
            return load_MultFromStr(list_,skipData = skipData)
        else:
            if len(list_) == 1:
                if glob.has_magic(st):
                    return [load_fileFromStr(list_[0],skipData = skipData)]
                else:
                    return load_fileFromStr(list_[0],skipData = skipData)
            else:
                print "no such file found : " + st
#        if os.path.isdir(str):
#            return load_dirFromStr(str)
#       else:
#           return load_fileFromStr(str)
    else:
        return load_MultFromStr(st,skipData = skipData)
        
################################ add here new saveble objects
def registerAsExtension(type_):
    Saveable.ext[type_.__EXT__] = type_
    return type_



print "loadSave imported"
