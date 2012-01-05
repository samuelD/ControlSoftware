from ..core.newSession import session,listen
from ..core import Spectrum,fit
import numpy as np
import scipy.constants as cst
from numpy import pi
from numpy import sqrt
from ..core.plotting import plot
from ..core.loadSave import load
from ..core.utils.Unit import Hz,K,kg,m,nm,V,s,mW,addDefaultUnit
from ..core.utils import Unit
from ..core import utils
from PyQt4.QtCore import QThread
from ..hardware.hardwareDevices import *
from numpy import *
from .. import *

#if utils.isHe3():
try:
    from ..hardware.daqmx import setShutters,setShutter,getShutter,getShutters
except WindowsError as e:
    print e

k = cst.k*m**2*kg*s**(-2)*K**(-1)
hbar = cst.hbar*m**2*kg*s**(-1)
c = cst.c*m/s
### see /He3/PhaseModulationCalibrations
def meff(sp, cal_mV_eff = 5, V_pi = 7.1, askFit = True,r = 25e-6,lambda_nm = 1550,T = 293):
    f = sp.fitter
    if not isinstance(sp.fitter,fit.FitterLorentzAndGauss):
        if askFit:
            yn = "dummy"
            while yn is not "y":
                yn = raw_input("spectrum %s was fitted with model %s. refit it with model \"LorentzGauss\"(y/n)?"%(sp.name,f.ID_STR))
                if yn =="n":
                    raise ValueError("spectrum should be fitted with LorentzGauss for determining effective mass")
        sp.fit(model = "LorentzGauss")

    ratio = sp["area_2"]/sp["area"]
    
    beta = np.pi*cal_mV_eff*0.001/V_pi
    
    omega = 2.0*np.pi*cst.c/(lambda_nm*1e-9)
    G = omega/r
    Omega = 2.0*np.pi*sp["x0_2_hz"]

    m = cst.k*T*(G**2)*ratio/((beta*Omega**2)**2)
    return m


def g0_hz(sp,cal_Veff = 5e-3, V_pi = None, askFit = True,T = 293,PM_calib_file = "M:\\phaseModulationCalibrations\\V_pi1550.spe"):#V_pi = 7.1
    """units in the arguments are now accepted, 
    if V_pi is not provided, it will use the calibration
    file specified by PM_calib_file"""
    
    cal_Veff = addDefaultUnit(cal_Veff,V)
    T = addDefaultUnit(T,K)
    f = sp.fitter
    if not isinstance(sp.fitter,fit.FitterLorentzAndGauss):
        if askFit:
            yn = "dummy"
            while yn is not "y":
                yn = raw_input("spectrum %s was fitted with model %s. refit it with model \"LorentzGauss\"(y/n)?"%(sp.name,f.ID_STR))
                if yn =="n":
                    raise ValueError("spectrum should be fitted with LorentzGauss for determining effective mass")
        sp.fit(model = "LorentzGauss")


    if V_pi == None:
        f = load(PM_calib_file)
        V_pi = utils.misc.interpFromPlottable(f,sp["x0_2_hz"])
    else:
        V_pi = 7.1
    V_pi = addDefaultUnit(V_pi,V)
    print "value of V_pi used is " + str(V_pi)

    ratio = sp["area_2"]/sp["area"]
    
    phi0 = np.pi*cal_Veff*sqrt(2)/V_pi
    
#    omega = 2.0*np.pi*cst.c/(lambda_nm*1e-9)

    Omega = 2.0*np.pi*sp["x0_2_hz"]*Hz

    nbar = k*T/(hbar*Omega)
    g0 = ((Omega**2*phi0**2)/(4*nbar*ratio))**.5/(2*pi)
    yn = raw_input("would you like results to be pasted in Origin to be copied in clipboard? [y]/n")
    if yn is not "n":
        #import utils
        utils.misc.copyToClipboard(str(sp["x0_hz"]*1e-6) +"\t"+str(sp["gamma_hz"]) + "\t"+"0" +"\t"+ str(g0.asNumber()))
    return g0


def g0_hz_from_m(m,lambda_nm = 1550,f_mech=70e6,r = 20e-6):
    f_mech = Unit.addDefaultUnit(f_mech,Unit.Hz)
    r = Unit.addDefaultUnit(r,Unit.m)
    lambda_nm = Unit.addDefaultUnit(lambda_nm,Unit.nm)
    m = Unit.addDefaultUnit(m,Unit.kg)

    Omega=f_mech*2*pi
    omega = 2.0*np.pi*cst.c*(Unit.m/Unit.s)/(lambda_nm)
    G = omega/r
    hbar = cst.hbar*Unit.m**2*Unit.kg/Unit.s
    return ((1.0/m)*hbar*G**2/(2*Omega))**.5*1/(2*np.pi)

def m_from_g0_hz(g0_hz,lambda_nm = 1550,f_mech=70e6,r = 20e-6):
    Omega=f_mech*2*pi
    g0 = g0_hz*2*pi
    omega = 2.0*np.pi*cst.c/(lambda_nm*1e-9)
    G = omega/r
    return 1.0/g0**2*cst.hbar*G**2/(2*Omega)

def S_nu_nu_of_f_pic_single_sided(sp,cal_mV_eff = 5, V_pi = 7.1, askFit = True):
    f = sp.fitter
    if not isinstance(sp.fitter,fit.FitterLorentzAndGauss):
        if askFit:
            yn = "dummy"
            while yn is not "y":
                yn = raw_input("spectrum %s was fitted with model %s. refit it with model \"LorentzGauss\"(y/n)?"%(sp.name,f.ID_STR))
                if yn =="n":
                    raise ValueError("spectrum should be fitted with LorentzGauss for determining effective mass")
        sp.fit(model = "LorentzGauss")

#   ratio = sp["area_2"]/sp["area"]
    
    phi0 = np.pi*cal_mV_eff*sqrt(2)*0.001/V_pi
    
#    omega = 2.0*np.pi*cst.c/(lambda_nm*1e-9)

    Omega = 2.0*np.pi*sp["x0_2_hz"]

#    nbar = cst.k*T/(cst.hbar*Omega)

    Snunu = Omega**2*phi0**2/(8*pi**2*1.06*sp["gamma_2_hz"])
    
    return Snunu

    
    
    
def nFinal(Pin,g0_hz,gamma_hz,Omega_hz,lambda_g0_nm = 1550,T = 0.8,lambda_nm = 780):
    gamma_hz = addDefaultUnit(gamma_hz,Hz)
    gamma = gamma_hz*2*pi
    g0_hz = addDefaultUnit(g0_hz,Hz)
    g0 = g0_hz*2*pi
    Omega_hz = addDefaultUnit(Omega_hz,Hz)
    Omega = 2*pi*Omega_hz
    lambda_ = addDefaultUnit(lambda_nm,nm)
    lambda_g0 = addDefaultUnit(lambda_g0_nm,nm)
    Pin = addDefaultUnit(Pin,mW)
    #c = cst.c*m/s
    T = addDefaultUnit(T,K)
    
    return (gamma*k*T*Omega*2*pi*c/lambda_*lambda_**2/(4*Pin*(g0)**2*lambda_g0**2)).asNumber()

def plot_Snunu_s_sided(sp,cal_mV_eff = 5, V_pi = 7.1, T = 293,askFit = True):
    Snunu = S_nu_nu_of_f_pic_single_sided(sp,cal_mV_eff = cal_mV_eff, V_pi = V_pi,askFit = askFit,T = T)
    peakValue = sp["area_2"]/(sp["gamma_2_hz"]*1.06)
    fact = Snunu/peakValue
    plot(sp.X,fact*sp.Y,unit_x = sp.unit_x,name_y = "S_vv(f) in Hz2/Hz",unit_y = Hz**2/Hz,win = "frequency noise spectrum")
       
       
def plot_Sxx_s_sided(sp,cal_mV_eff = 5, V_pi = 7.1, askFit = True,r = 20e-6,lambda_nm = 780):
    Snunu = S_nu_nu_of_f_pic_single_sided(sp,cal_mV_eff = cal_mV_eff, V_pi = V_pi,askFit = askFit)
    peakValue = sp["area_2"]/(sp["gamma_2_hz"]*1.06)
    nu = cst.c/(lambda_nm*1e-9)
    dnu_sur_dl = nu/r
       
       
    fact = Snunu/peakValue*(1/dnu_sur_dl)**2
    plot(sp.X,fact*sp.Y,unit_x = sp.unit_x,name_y = "S_xx(f)",unit_y = m**2/Hz,win = "frequency noise spectrum")


def niceFourrier(sp,fft,):
    import pylab as p
    p.subplot(211)
    plot(sp.X,sp.Y,win = "p")
    p.xlabel("time (s)")
    p.ylabel("sig.")
    p.subplot(212)
    plot(fft.X,fft.Y,win = "p")
    p.xlabel("freq (Hz)")
    p.ylabel("Fourier transform")
    p.show()
    
    
def overlap(Vpp,LO,sig):
    return Vpp/(2*sqrt(LO * sig))

def triggerAndWait(s):
    s.write("ACQ:STOPA SEQ")
    s.write("ACQ:State RUN")
    while int(s.ask("ACQ:State?")):
        QThread.msleep(20)
        
def autoScale(s):
    s.write("ACQ:STOPA SEQ")
    s.setPosition(0.0)
    s.write("ch%i:Offset 0.0"%s.getChannel())
    done=False
    f=0.0
    while done==False:
        triggerAndWait(s)
        data=s._getYvalues_()
        if ((max(data)==253) | (min(data)==2)):
            a=float(s.ask("ch%i:scale?"%s.getChannel()))
            f=a*8.0
            s.write("ch%i:scale %f"%(s.getChannel(),f))
            disp(">")
        elif ((max(data)<168) & (min(data)>88)):
            fplus=128.0/abs(max(data)-128)
            fminus=128.0/abs(128.0-min(data))
            a=float(s.ask("ch%i:scale?"%s.getChannel()))
            f=a/(min([fplus, fminus])*.6)
            s.write("ch%i:scale %f"%(s.getChannel(),f))
            disp("<")
        else:            
            done=True
            disp("XXXXX")
        s.write("ACQ:STOPA RUNST")
    
    
def getOverlap_AI(Ch = 2, confirmDangerous = True, t_sleep=30, n = 2000, samplerate=200000):
    from ..hardware.daqmx import do,ao,ai
    setShutters("homodyne",confirmDangerous=confirmDangerous)
    QThread.msleep(t_sleep)
    V=ai.readValues(Ch, n=n, samplerate=samplerate)
    Vminx = V.argmin()
    Vminy = mean(V[Vminx-2:Vminx+2]) #average local environment of minimum 
    Vmaxx = V.argmax()
    Vmaxy = mean(V[Vmaxx-2:Vmaxx+2]) #average local environment of minimum
    Vhom = Vmaxy-Vminy
    disp(Vhom)
    setShutters("balanceDetectors")
    setShutter("detectorMinus",1)
    setShutter("detectorPlus",0)
    QThread.msleep(t_sleep)
    
    V=ai.readValues(Ch, n=n, samplerate=samplerate)
    VLOplus = mean(V)
    disp(VLOplus)
    setShutter("detectorMinus",0)
    setShutter("detectorPlus",1)
    QThread.msleep(t_sleep)
    
    V=ai.readValues(Ch, n=n, samplerate=samplerate)
    VLOminus = mean(V)
    disp(VLOminus)
    setShutter("LO",1)
    setShutter("signal",0,confirmDangerous=confirmDangerous)
    QThread.msleep(t_sleep)
    
    V=ai.readValues(Ch, n=n, samplerate=samplerate)
    Vsigminus = mean(V)
    disp(Vsigminus)
    setShutter("detectorMinus",1)
    setShutter("detectorPlus",0)
    QThread.msleep(t_sleep)
    
    V=ai.readValues(Ch, n=n, samplerate=samplerate)
    Vsigplus = mean(V)
    disp(Vsigplus)
    
    setShutters("homodyne",confirmDangerous=confirmDangerous)
    return overlap(Vhom,(VLOplus-VLOminus)*2,(Vsigplus-Vsigminus)*2)

def scatteringOverlap(repeat = 100):
    array=zeros(repeat)
    for i in arange(0,repeat):
        array[i]=getOverlap_AI(Ch = 2, confirmDangerous = False, n = 10000, samplerate=200000)
    return array
    
def getOverlap(Ch = 1, PowerBalanced = False, confirmDangerous = True):
    s = defaultDevice("SCOPE")
    s.setChannel(Ch)
    temp=s.getV_div()
    setShutters("balanceDetectors")
    s.write("ACQ:STOPA RUNST")
    s.write("ACQ:State RUN")
    if PowerBalanced == False:
        raw_input("balance power now, then press enter")
        
    setShutters("homodyne",confirmDangerous=confirmDangerous)
    QThread.msleep(30)
    s.autoScale(keepTrace=True)
    #triggerAndWait(s)
    V = s.getTrace()
    Vminx = V.Y.argmin()
    Vminy = mean(V.Y[Vminx-5:Vminx+5]) #average local environment of minimum 
    Vmaxx = V.Y.argmax()
    Vmaxy = mean(V.Y[Vmaxx-5:Vmaxx+5]) #average local environment of minimum
    Vhom = Vmaxy-Vminy
    disp(Vhom)
    setShutters("balanceDetectors")
    setShutter("detectorMinus",1)
    setShutter("detectorPlus",0)
    QThread.msleep(30)
    s.autoScale(keepTrace=True)
    #triggerAndWait(s)
    V = s.getTrace()
    VLOplus = mean(V.Y)
    disp(VLOplus)
    setShutter("detectorMinus",0)
    setShutter("detectorPlus",1)
    QThread.msleep(30)
    s.autoScale(keepTrace=True)
    #triggerAndWait(s)
    V = s.getTrace()
    VLOminus = mean(V.Y)
    disp(VLOminus)
    setShutter("LO",1)
    setShutter("signal",0,confirmDangerous=confirmDangerous)
    QThread.msleep(30)
    s.autoScale(keepTrace=True)
    #triggerAndWait(s)
    V = s.getTrace()
    Vsigminus = mean(V.Y)
    disp(Vsigminus)
    setShutter("detectorMinus",1)
    setShutter("detectorPlus",0)
    QThread.msleep(30)
    s.autoScale(keepTrace=True)
    #triggerAndWait(s)
    V = s.getTrace()
    Vsigplus = mean(V.Y)
    disp(Vsigplus)
    s.write("ACQ:STOPA RUNST")
    s.write("ACQ:State RUN")
    s.setV_div(temp)
    setShutters("homodyne",confirmDangerous=confirmDangerous)
    return overlap(Vhom,(VLOplus-VLOminus)*2,(Vsigplus-Vsigminus)*2)

def balancePowers():
    #from daqmx import setShutters,setShutter
    setShutters("balanceDetectors")
    raw_input("balance power now, then press enter")
    setShutter("detectorMinus",1)
    VLOplus = input("enter voltage LO+ as read on the scope")
    
    setShutter("detectorMinus",0)
    setShutter("detectorPlus",1)
    VLOminus = input("enter voltage LO- as read on the scope")
    
    setShutter("LO",1)
    setShutter("signal",0)
    Vsigminus = input("enter voltage sig- as read on the scope")
    
    setShutter("detectorMinus",1)
    setShutter("detectorPlus",0)
    Vsigplus = input("enter voltage sig+ as read on the scope")
    
    setShutters("homodyne")
    Vhom = input("enter Vpp homodyne from the scope")
    
    
    return overlap(Vhom,(VLOplus-VLOminus)*2,(Vsigplus-Vsigminus)*2)
   
def quickSNR(name):
    e = defaultDevice("ESA")
    s = e.quickTrace(name,isFit = True)
    return SNR(s)
        
def SNR(s):
    return 10*log10((s["area"]/s["gamma_hz"])/s.Y[0:len(s.Y)/10].mean())


def occupation(T,nu_mech):
    return cst.k*T/(cst.h*nu_mech)



def getDetuningSweepPointValues(sp,na_amp,nu_mech = 78e6,widthEIT = 4.0e6,calib = 1.0):
    EITstart = nu_mech - widthEIT/2
    EITstop  = nu_mech + widthEIT/2
    nph = calib*(sp["area"])/((na_amp.mean(EITstart-1e6,EITstart)+na_amp.mean(EITstop,EITstop + 1e6))/2)
    return (na_amp["delta_hz"],sp["x0_hz"],sp["gamma_hz"],nph)


    
    
def treatDetuningSweep(directory = ".",name = None,pattern = "*.spe",nu_mech = 78.1e6,widthEIT = 4e6,calib = 1.0,style = "D-",**kwds):
    import os
    from .. import loadSave
    
    if name is None:
        name = directory
    occ = plot(win = "occupancy",name = name,style = style,**kwds)
    damp = plot(win = "damping",name = name,style = style,**kwds)
    detuning = plot(win = "detuning",name = name,style = style,**kwds)
    occOfDamp = plot(win = "occOfDamp",name = name,style = style,**kwds)
    spes = loadSave.load(os.path.join(directory,"*ESA" + pattern),skipData = True)
    nas = loadSave.load(os.path.join(directory,"*NA_amp" + pattern))
    
    for sp,na_amp in zip(spes,nas):
#        sp.fit(model = "Lorentz",excludeXRegion = [max(sp.X)-(max(sp.X)-min(sp.X))*0.1,max(sp.X)])
#       na_amp.fit(model = "splittedNA",usePanelParams = True)
#        det = na_amp["delta_hz"]
        
#       EITstart = nu_mech - widthEIT/2
#      EITstop  = nu_mech + widthEIT/2
#     nph = calib*(sp["area"])/((na_amp.mean(EITstart-1e6,EITstart)+na_amp.mean(EITstop,EITstop + 1e6))/2)
        
        (det,fs,damping,nph) = getDetuningSweepPointValues(sp,na_amp,calib = calib,widthEIT = widthEIT,nu_mech = nu_mech)     
        
        detuning.appendPoint(fs,det)
        damp.appendPoint(damping,det)
        occ.appendPoint(nph,det)
        occOfDamp.appendPoint(nph,damping)
        occ.plot()
        detuning.plot()
        damp.plot()
        occOfDamp.plot()
    yn = raw_input("do you want to save the 3 produced plots in the same directory? (y/n)")    
    if yn == "y":
        detuning.save(path = directory)
        damp.save(path = directory)
        occ.save(path = directory)
        

from time import sleep

@session
def someSession(param1 = (1,2),_param2 = 6,_param3 = (4,3),_param4 = 4):
    """this is a session"""
    for i in range(100):
        listen()
        plot([1,param2,4,param4,3,4])
        sleep(1)
        print "live " +  str(param4)
        print "static "  + str(_param4)
        
    