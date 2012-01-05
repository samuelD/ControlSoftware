from unum.units import Hz,kg,g,mg,ug,ng,pg,V,m,mm,um,nm,K,mK,uK,nK,BAR,N,s,ms,us,ns,W,A,mA,uA,nA,J,rad,deg
from unum import IncompatibleUnitsError,ShouldBeUnitlessError
import math
from unum import Unum
import numpy
import re #regular expressions for helping recognize strange units
#mBAR =  Unum.unit("mBar",1e-3*BAR)

mHz = Unum.unit("mHz",0.1*Hz)
kHz = Unum.unit("kHz",1000*Hz)
MHz = Unum.unit("MHz",1e6*Hz)
GHz = Unum.unit("GHz",1e9*Hz)

mW = Unum.unit("mW", 1e-3*W)
uW = Unum.unit("uW", 1e-6*W)
nW = Unum.unit("nW", 1e-9*W)
pW = Unum.unit("pW", 1e-12*W)

mV = Unum.unit("mV",1e-3*V)
uV = Unum.unit("uV",1e-6*V)
#nV = Unum.unit("nV",1e-9*V)



mrad = Unum.unit("mrad",1e-3*rad)

dBm = Unum.unit("dBm")




def getName(u):
    if isUnit(u,Hz):
        return "frequency"
    if isUnit(u,s):
        return "time"
    if isUnit(u,dBm):
        return "power"
    if isUnit(u,kg):
        return "mass"
    if isUnit(u,V):
        return "voltage"
    if isUnit(u,K):
        return "temperature"
    if isUnit(u,BAR):
        return "pressure"
    if isUnit(u,m):
        return "length"
    if isUnit(u,rad):
        return "phase"
    if isUnit(u,deg):
        return "phase"
    return ""


def dBm2Veff(val):
    """returns val in units of Volts (assuming of course 50 Ohm impedance)"""
    if not isinstance(val,numpy.ndarray):
        val = addDefaultUnit(val,dBm)
        val = inUnit(val,dBm)*1.0	
        return numpy.sqrt(10**(val/10)*0.001*50)*V
    else:
        return numpy.sqrt(10**(val/10)*0.001*50)
        
def dBm2W(val):
    """returns val in units of W"""
    if not isinstance(val,numpy.ndarray):
        val = addDefaultUnit(val,dBm)
        val = inUnit(val,dBm)*1.0	
        return 10**(val/10)*0.001*W
    else:
        return 10**(val/10)*0.001
    
    
def dB2Number(val):
    if not isinstance(val,numpy.ndarray):
        val = addDefaultUnit(val,dBm)
        val = inUnit(val,dBm)*1.0    
        return 10**(val/10)
    else:
        return 10**(val/10)

def dBm2Veff_sq(val):
    """returns val in units of Volts square (assuming of course 50 Ohm impedance)"""
    if not isinstance(val,numpy.ndarray):
        val = addDefaultUnit(val,dBm)
        val= inUnit(val,dBm)*1.0	
        return 10**(val/10)*0.001*50*V**2
    else:
        return 10**(val/10)*0.001*50

def Veff_sq2dBm(val):
    """returns val in units of Volts square (assuming of course 50 Ohm impedance)"""
    if not isinstance(val,numpy.ndarray):
        val = addDefaultUnit(val,V**2)
        val= inUnit(val,V**2)*1.0
        return 10*numpy.log10(val/50*1000)*dBm
    else:
        return 10*numpy.log10(val/50*1000)

#def Veff_sq2dBm_array(val):
 #   return 10*numpy.log10(val/50*1000)


def Veff2dBm(val):
    """returns val as a number (without unum unit) in dBm with unit "1" (assuming of course 50 Ohm impedance)"""
    if not isinstance(val,numpy.ndarray):
        val = addDefaultUnit(val,V)
        val = inUnit(val,V)*1.0	
        return 10*numpy.log10(val**2/50*1000)*dBm
    else:
        return 10*numpy.log10(val**2/50*1000)

def isUnit(val,u):
    if isNum(val):
        if isNum(u):
            return True
        else:
            return False
    try:
        val.asUnit(u)
    except IncompatibleUnitsError:
        return False
    return True

def isNum(val):
    try:
        val.checkNoUnit()
    except ShouldBeUnitlessError:
        return False
    except AttributeError:
        try:
            2+val
        except TypeError:
            return False
        return True
    return True

def addDefaultUnit(val,u):
    if isNum(val):
        return val*u
    if not isUnit(val,u):
        raise IncompatibleUnitsError(val,u)
    return val
        

def inUnit(val,u):
    if isNum(u):
        if isNum(val):
            return val
        else:
            raise IncompatibleUnitsError(val,m/m)
    if isNum(val):
        if isNum(u):
            return val
        else:
            raise IncompatibleUnitsError(u,m/m)
    return val.asUnit(u).asNumber()

def getUnit(val):
    return val/val.asNumber()

def unitStr(u):
    if isNum(u):
        return ""
    return u.strUnit()[1:-1]
    

def addPower(match):
    str = match.group()
    return str[0] + "**" + str[1]

def unitFromStr(str):
    if str == "":
        return None
    str = re.sub("[A-z][0-9]",addPower,str)
    str = re.sub("\.","*",str)
    return eval(str)

def unitUp(u):
    if u is Hz:
        return kHz
    if u is kHz:
        return MHz
    if u is MHz:
        return GHz
    return u

def unitDown(u):
    if u is W:
        return mW
    if u is mW:
        return uW
    if u is uW:
        return nW
    if u is nW:
        return pW
   
    if u is Hz:
        return mHz
    
    return u

def upgradeUnit(u,n):
    """gives the unit n*10**3 times larger"""
    if n>0:
        for i in range(n):
            u = unitUp(u)
    if n<0:
        for i in range(-n):
            u = unitDown(u)
    return u    
    
def checkCompatible(u1,u2):
    inUnit(u1,u2)
print "Unit imported"

def toSI(u):
    if isUnit(u,dBm):
        return dBm2W(u)
    newUnit = SIunit(u)
    return inUnit(u,newUnit)*newUnit

def SIunit(u):
    if isUnit(u,J):
        return J
    if isUnit(u,W):
        return W
    if isUnit(u,Hz):
        return Hz
    if isUnit(u,dBm):
        return W
    if isNum(u):
        return 1
    if isUnit(u,m):
        return m
    if isUnit(u,kg):
        return kg
    if isUnit(u,s):
        return s
    if isUnit(u,V**2):
        return V**2
    if isUnit(u,V):
        return V
    if isUnit(u,rad):
        return rad
    if isUnit(u,deg):
        return rad
    if isUnit(u,K):
        return K
    raise NotImplementedError("don't know yet how to convert composed units into SI")


def asNum(u):
    if isNum(u):
        return u
    return u.asNumber()

def toSINumber(val):
    return toSI(val).asNumber()
    
