
import os
#try: 
#    import visa
#except (OSError,ImportError):
#    pass
#import hardwareDevices

import path
confDir = path.getConfDir()#os.path.join(os.path.dirname(__file__),"conf")
confPath = path.getPathFile()#os.path.join(confDir,"path.cfg")
confHardware = path.getHardwareFile()#os.path.join(confDir,"hardware.cfg")


def getAllHardwareNames():
    return _getAllNames_(confHardware)


def updateHardware(newName,newDevice,newAddress):
    names = getAllHardwareNames()
    address = map(lambda x: defaultDeviceAddress(x)[1],names)
    if not (newAddress in address):
        with open(confHardware,"a") as f:
            f.write(newName + " = " + newDevice + "@" + newAddress + "\n")
            

def _getAllNames_(fileName):
    allNames = [] 
    try:
        f = open(fileName)
        l = f.readline()
        while l!="":
            doublet = l.split("=")
            if len(doublet) != 2:
                continue
            (n,val) = (doublet[0].rstrip(),doublet[1].lstrip().rstrip("\n"))
            allNames.append(n)
            l = f.readline()
    except IOError:
        pass
    return allNames

def _readSomeValue_(fileName,name):
    try: 
        f = open(fileName)
        l = f.readline()
        while l!="":
            doublet = l.split("=")
            (n,val) = (doublet[0].rstrip(),doublet[1].lstrip().rstrip("\n"))
            if n == name:
                return val
            l = f.readline()
    except IOError:
        return ""
    

def defaultLoadDir():
    return _readSomeValue_(confPath,"defaultLoadDir")
     
def analysisPath():
    return _readSomeValue_(confPath,"analysisPath")
       
def saveDir():
    return _readSomeValue_(confPath,"saveDir")


def defaultDeviceAddress(name):
    """returns the default device of type name as specified in defaultHardware.cfg"""
    str = _readSomeValue_(confHardware,name)
    str = str.split("@")
    className = str[0].strip()
    adress = str[1].strip()
    return (className,adress)#eval("hardwareDevices.%s(\"%s\")"%(className,adress))

        
print "readConfig imported"
