from .. import *
import scipy
import numpy
from numpy import floor

@session
def AbsolutPMCalibration(isPlot = False,RF_N = 15, RF_start=10*MHz, RF_stop=150*MHz, Veff_N=10, Veff_start=100*mV, Veff_stop=1*V):        
        """
        RF_N: Number of linearly spaced frequencies where data are taken at, spanning
        linearly from RF_start to RF_stop
        Power_N: Number of different power levels to be measured at a given frequency 
        spanning linearly from Power_start to Power_stop
        Make sure you see a few fringes on the scope. On the very edge the (Fourierdomain) smoothening
        causes problems
        """
        rs = defaultDevice("FreqGen")
        osc = defaultDevice("SCOPE")
        tr=osc.getTrace(saveInAutoGenDir=False,saveCSVcopy=False)
        points=len(tr.X)
        filt=scipy.signal.get_window(("gaussian",points/1000),points,fftbins=True)
        filt=scipy.fftpack.ifftshift(filt)

        for i in range(RF_N):
            freq=RF_start+i*(RF_stop-RF_start)/(RF_N-1)
            rs.setFreq(freq)
            a=[]
            for j in range(Veff_N):
                Veff=Veff_start+j*(Veff_stop-Veff_start)/(Veff_N-1)
                rs.setVeff(Veff)
                osc.write("ACQuire:STATE ON")
                sleep(0.1)
                tr=osc.getTrace(saveInAutoGenDir=False,saveCSVcopy=False)
                #(b,a) = signal.butter(2,0.005,btype = "low") # second order low pass filter for X...
                #trD_Y = signal.lfilter(b,a,tr.Y)
                tr.X=tr.X-tr.X[0]
                trD_Y=tr.Y[1::100]#scipy.signal.resample(tr.Y, points/10, t=None, axis=0, window=("gaussian",10))
                trD_X=tr.X[1::100]
                trD_X=trD_X
                trD=plotting.Fittable(X=trD_X,Y=trD_Y)
                trD.fit(model="Cos", plotAfterwards=isPlot)
                
                phi0=trD["phi"]
                dt=tr.X[1]-tr.X[0] #timestep between datapoints
                dT=tr.X[-1]-tr.X[0] #time span
                Tpi=.5/trD["x0_hz"] #time between two zeros
                npi=Tpi/dt #number of datapoints between two zeros
                N=int(floor(trD["x0_hz"]*dT*2))-2 #Number of zeros to be used on trace                
                
                n=numpy.arange(0,N-1)
                if phi0<0:
                    phi0=phi0+numpy.pi
                center=floor((2.0-(phi0%numpy.pi)/numpy.pi-.5+int(floor(N/2)))*npi)
                fSI=Unit.toSI(freq)
                fSI=fSI.asNumber()
                VSI=Unit.toSI(Veff)
                VSI=VSI.asNumber()
                start=center-int(10/(fSI*dt))
                stop=center+int(10/(fSI*dt))
                trRF_X=tr.X[start:stop]
                trRF_Y=tr.Y[start:stop]
                trRF_X=trRF_X-trRF_X[floor(len(trRF_X)/2)]
                trRF=plot(X=trRF_X,Y=trRF_Y)
                trRF.fit(model="CosPlusLin", plotAfterwards=isPlot)
                
                temp=[fSI, VSI, trD["x0_hz"], trD["phi"], trD["amplitude"],trD["offset"],trRF["x0_hz"], trRF["phi"], trRF["amplitude"],trRF["offset"],trRF["slope"]]
                a.append(temp)
                
            numpy.savetxt("M:\\phaseModulationCalibrations\\2010-10-12_1550PM_AbsolutCalibration\\%d.csv"%fSI,a, delimiter=",")












def smartScaleSpan(factor):
    e = defaultDevice("ESA")
    newSpan = factor*e.getSpan()
    print "press Enter please (I have something to ask)"
    print "\a"
    yn = raw_input("I am about to multiply the span by %f (%s), are you OK ([y]/n)"%(factor,newSpan))
    if yn=="y"or yn=="":
        e.setRBWAuto()
        e.setSpan(newSpan)
        rbw = inUnit(e.getRBW(),Hz)
        if rbw > 100 and rbw < 2000:
            e.setRBW(100)
        return True
    return False
    
def focusOnTrace(sp):
    e = defaultDevice("ESA")
    change = False
    if abs(sp["x0_hz"]-inUnit(e.getCenter(),Hz))>inUnit(e.getSpan(),Hz)/15:
        change = smartSetCenter(sp["x0_hz"]) or change
    if sp["gamma_hz"]*8>inUnit(e.getSpan(),Hz):
        change = smartScaleSpan(2.0) or change
    if sp["gamma_hz"]*20<inUnit(e.getSpan(),Hz):
        change = smartScaleSpan(0.5) or change
    return change
 
def smartSetCenter(newCenter):    
    e = defaultDevice("ESA")
    print "press Enter please (I have something to ask)"
    print "\a"
    yn = raw_input("I am about to set the center at %s are you OK ([y]/n)"%(newCenter))
    if yn=="y"or yn=="":
        e.setCenter(newCenter)
        return True
    return False




def takeSBsweep(theName,averagingTime,powerSBsweep_dBm,isFitTrace = True):#nu_mech = 0,widthEIT = 0
    print "1) taking a SB sweep"
    na = defaultDevice("NA")   
    na.recallState("SBsweep_averages")
    na.setPower(powerSBsweep_dBm*dBm)
    powCal = na.getPower()
    
    na.trigger()
    sleep(averagingTime)

    #while int(na.ask(":INIT1:CONT?"))==1:    
    #    print "waiting"
    na.setCurrTrace(1)
    na_amp=na.getTrace()
    
    #na_amp.save()
    #na_amp.removeSegmentX(EITstart,EITstop)
    
    if isFitTrace:
        #EITstart = nu_mech - widthEIT/2
        #EITstop  = nu_mech + widthEIT/2
        #try:
        #na_amp.fit(usePanelParams = False,model = "Lorentz",plotAfterwards = False,excludeXRegion = [EITstart,EITstop],verboseLevel = 0)
        na_amp.fit(usePanelParams = True,model = "splittedNA",plotAfterwards = False,verboseLevel = 0)
        #except:
        #   print "Error during fit"
    na_amp.plot(win="NA_amp", name="NA_amp_"  + theName)
    
    na.setCurrTrace(2)
    na_phi=na.getTrace()
    na_phi.setWin("NA_phi")
    na_phi.plot(win="NA_phi", name="NA_phi_" + theName)
    
    na_phi.setName(name="NA_phi_" + theName)
    na_phi.save()
    na_amp.save()
    return (na_amp,na_phi)

lastPara = None
lastModel = None 

def takeSpectrum(theName,peakFreqs,peakMinWidths,pow,calON,averageTime,reuseLastFit,isRestart = True):
    
    #peakFreqs = getPeakFreqs()
    #peakMinWidth = getPeakMinWidth()
    
    global lastPara
    global lastModel
    
    e = defaultDevice("ESA")
    na = defaultDevice("NA")
    na.recallState("calpeak")
    #na.setOutputOn(False)
    calFreq = (e.getStop()-e.getSpan()/20).asNumber()
    na.setCenter(calFreq)
    #pow = getDV("powCal (dBm)")
    na.setPower(pow)
    #calON = getDV("calibrationON")
    na.setOutputOn(calON)
    if calON:
        calOnOffStr = "calON"
    else:
        calOnOffStr = "calOFF"
    na.trigger() #trigger single trace
 
    sleep(1.000)
    
    if isRestart:
        e.restart()
    print "2) taking the spectrum"
    timeSleep = int(averageTime)
    sleep(timeSleep)
    #if lastPara is not None:
    #    lastPara = sp.fitter.param_fitted
    #    lastModel = sp.fitter.ID_STR
    sp = e.getTrace()
    sp.setName("ESA_" + theName +"_"+ calOnOffStr)
    
    #dvs = getAllDV()
    i = 0
#        while True:
#            i = i+1
#            try:
#                peak = ["peak" + str(i)]
#                width = dvs["width" + str(i)]
#            except KeyError:
#                break
    
    bw = Unit.inUnit(e.getRBW(),Hz)
    width = 3*bw
    for peak in peakFreqs:
        sp.removeSegmentX(peak - width/2,peak + width/2)
        #sp.removeSegmentX(peak2 - width/2,peak2 + width/2)
    
    if reuseLastFit and lastPara is not None:
        sp.fit(model = lastModel,param_free = lastPara,plotAfterwards = False,verboseLevel = 0,excludeXRegion = [calFreq-e.getSpan().asNumber()/20,calFreq+e.getSpan().asNumber()/20])
    else:
        sp.fit(model = "Lorentz",plotAfterwards = False,verboseLevel = 0,excludeXRegion = [calFreq-e.getSpan().asNumber()/20,calFreq+e.getSpan().asNumber()/20])
    lastPara = sp.fitter.param_fitted
    lastModel = sp.fitter.ID_STR
        
    sp.plot(win = "spectra")
    sp.save()

    
    calPeak0span = na.getTrace()
    calPeak0span.truncateX(timeSleep)
    calPeak0span.setName(name = "calPeak0span" + theName)
    calPeak0span.save()
    e.write("*sav 8")
    return (sp,calPeak0span)

#def getPeakFreqs(self):
#    i = 1
#    l = []
#    while(True):
#        try:
#            val = getDV("peak%i"%i)
#        except AttributeError:
#            break
#        i += 1
#        l.append(val)
#    return l

#def getPeakMinWidth(self):
#    i = 1
#    l = []
#    while(True):
#        try:
#            val = getDV("peak%i_minWidth"%i)
#        except AttributeError:
#            break
#        i += 1
#        l.append(val)
#    return l

def takeLargeSpan(theName,averageTime):
    na = defaultDevice("NA")
    e = defaultDevice("ESA")
    ####################################################
    ## switch the NA to output nothing                   ##
    ####################################################
    na.recallState(2)
    na.write("output off")
    
    e.write("*rcl 9")
    print "3) taking a largeSpan"
    sleep(averageTime)
    ls = e.getTrace()
    ls.setName("largeSpan_" + theName)
    ls.plot(win = "largeSpans")
    ls.save()
    return ls


def takeOnePoint(theName,averageIntermediate,nu_mech,widthEIT,calib,peakFreqs,peakMinWidths,isRestart = True):
    e = defaultDevice("ESA")
    na = defaultDevice("NA")
    
    ####################################################
    ##          set properly the cal peak             ##
    ####################################################
    
    (sp,calPeak0span) = takeSpectrum(theName,peakFreqs,peakMinWidths,isRestart = isRestart) 
    print "afterSpec"
    bw = e.getRBW()
    span = e.getSpan()
    range = [Unit.inUnit(e.getStart(),Hz),Unit.inUnit(e.getStop(),Hz)]
    
    ####################################################
    ##          sideband sweep on the NA              ##
    ##          should be defined on NA state 1       ##
    ####################################################
    (na_amp,na_phase) = takeSBsweep(theName)            
    print "afterSB"
    
    
    ####################################################
    ## take first a large span trace on the ESA       ##
    ## state 9 is the large span setting              ##
    ####################################################
    ls = takeLargeSpan(theName)
    bwLarge = e.getRBW()
    if(span<3*bwLarge):
        print "taking intermediate span"
        e.setCenter(nu_mech)
        e.setRBWAuto()
        sleep(averageIntermediate)
        e.setSpan(5e6)
        intermSp = e.getTrace()
        intermSp.setName("intermediateSpan_" + theName)
        intermSp.plot(win = "largeSpans",uncheckOthers = False,scaleOnMe = False)
        intermSp.save()
    
    ####################################################
    ## take traces of the spurious modes              ##                                ##
    ####################################################
    
    #peakFreqs = getPeakFreqs()
    #peakMinWidth = getPeakMinWidth()
    for fr,w in zip(peakFreqs,peakMinWidths):
        if fr>range[0] and fr<range[1]:
            print "taking spurious mode at freq. %d"%fr
            e.setCenter(fr)
#                    e.setRBW(100)
            newSpan = max(3*bw.asNumber(),w)
            e.setSpan(newSpan)
            sleep(averageSpurious)
            spurious = e.getTrace()
            spurious.setName("spuriousMode_freq%d_"%fr + theName)
            spurious.plot(win = "spectra",uncheckOthers = False,scaleOnMe = False)
            spurious.save()
    
    e.write("*rcl 8")     
    
    EITstart = nu_mech - widthEIT/2
    EITstop  = nu_mech + widthEIT/2
    nph = calib*(sp["area"])/((na_amp.mean(EITstart-1e6,EITstart)+na_amp.mean(EITstop,EITstop + 1e6))/2)
    na.recallState("quick+Zoom")
    
    return (sp,calPeak0span,na_amp,na_phase,nph)


@session
def detuningSweep(_step_V = -0.01,_averageSpectrum = 10,_powerCal = -10,_calON = True,_averagingTime_intermediate = 5,_averagingTime_spurious = 5,_averagingTime_SB = 10,_powerSBsweep_dBm = -10,_averagingTime_largeSpan = 5,_autopilot = True,_reuseLastFit = True,defaultStartingWidth = 100e3,nu_mech = 93.08e6,widthEIT = 4e6,calib = 200*1488.0/1400,peakFreqs = [92.68e6],peakMinWidths = [0.25e6]):
    nu_mech = nu_mech
    import visa
    lastPara = None
    lastModel = None 
    #first = True
    ####################################################
    ##          define the instruments                ##
    ####################################################
    e = defaultDevice("ESA")
    na = defaultDevice("NA")
    #e2 = visa.instrument("GPIB0::18")
    
    ####################################################
    ## check that ESA has the right startingParameters##
    ####################################################
    change = True
    
    
    print "press enter"
    yn = raw_input("Should I reset the ESA window around mechanical peak? [y]/n")
    if yn == "" and yn != "n":
        e.setRBWAuto()
        e.setSpan(defaultStartingWidth)
        rbw = inUnit(e.getRBW(),Hz)
        if rbw > 100 and rbw < 2000:
            e.setRBW(100)
        e.setCenter(nu_mech)
    #while change: 
    #    s = e.getTrace()
    #    s.fit()
    #    change = focusOnTrace(s)
        #s.remove()
    
    #print "press enter"
    #print "\a"
    #yn = raw_input("do you want to remove all traces ([y]/n)?")
    #if yn != "n":
    #    for w in plotManager.getWindows():
    #        for c in w.getCurves():
    #            c.remove()
    
    ####################################################
    ##          define the plots                      ##
    ####################################################
    detuning = plot(name = "detuning",win = "detuning",name_x = "Frequency",name_y = "optical spring",style = "-dr")
    gamma = plot(name = "damping",win = "damping",name_x = "Frequency",name_y = "damping",style = "-dg")
    nPhonons = plot(name = "occupancy",win = "occupancy",name_x = "Frequency",name_y = "occupancy",style = "-db")
    #thermoShift = plot(name = "thermoShift",win = "thermoShift",name_x = "Frequency",name_y = "shift thermometer mode",style = "-dr",scaleOnMe = False)
    
    ####################################################
    ##get the current value of the voltage            ##
    ##of piezo(AO ch 0)                               ##
    ####################################################
    V = hardware.daqmx.ao.getLastValue(0)  
    ####################################################
    ##          Main loop                             ##
    ####################################################
    while V>0:
        theName =  str(V) + "V"
        ####################################################
        ##          set laser voltage (slowly)            ##
        ####################################################
        listen()
        setV(V,slowly=True)
        e.restart()
        #(sp,calPeak0span,na_amp,na_phi,nph) = takeOnePoint(theName,nu_mech,widthEIT,calib,peakFreqs,peakMinWidths)
        ####################################################
        ##          set properly the cal peak             ##
        ####################################################
        listen()
        (sp,calPeak0span) = takeSpectrum(theName,peakFreqs,peakMinWidths,powerCal,calON,averageSpectrum,reuseLastFit) 
        print "afterSpec"
        bw = e.getRBW()
        span = e.getSpan()
        range = [Unit.inUnit(e.getStart(),Hz),Unit.inUnit(e.getStop(),Hz)]
        
        ####################################################
        ##          sideband sweep on the NA              ##
        ##          should be defined on NA state 1       ##
        ####################################################
        listen()
        (na_amp,na_phase) = takeSBsweep(theName,averagingTime_SB,powerSBsweep_dBm)            
        print "afterSB"
        
        
        ####################################################
        ## take first a large span trace on the ESA       ##
        ## state 9 is the large span setting              ##
        ####################################################
        ls = takeLargeSpan(theName,averagingTime_largeSpan)
        bwLarge = e.getRBW()
        if(span<3*bwLarge):
            listen()
            print "taking intermediate span"
            e.setCenter(nu_mech)
            e.setRBWAuto()
            sleep(averagingTime_intermediate)
            e.setSpan(5e6)
            intermSp = e.getTrace()
            intermSp.setName("intermediateSpan_" + theName)
            intermSp.plot(win = "largeSpans",uncheckOthers = False,scaleOnMe = False)
            intermSp.save()
        
        ####################################################
        ## take traces of the spurious modes              ##                                ##
        ####################################################
        
        #peakFreqs = getPeakFreqs()
        #peakMinWidth = getPeakMinWidth()
        for fr,w in zip(peakFreqs,peakMinWidths):
            if fr>range[0] and fr<range[1]:
                listen()
                print "taking spurious mode at freq. %d"%fr
                e.setCenter(fr)
    #                    e.setRBW(100)
                newSpan = max(3*bw.asNumber(),w)
                e.setSpan(newSpan)
                sleep(averagingTime_spurious)
                spurious = e.getTrace()
                spurious.setName("spuriousMode_freq%d_"%fr + theName)
                spurious.plot(win = "spectra",uncheckOthers = False,scaleOnMe = False)
                spurious.save()
        
        e.write("*rcl 8")     
        
        EITstart = nu_mech - widthEIT/2
        EITstop  = nu_mech + widthEIT/2
        nph = calib*(sp["area"])/((na_amp.mean(EITstart-1e6,EITstart)+na_amp.mean(EITstop,EITstop + 1e6))/2)
        na.recallState("quick+Zoom")
        
        
        
        ####################################################
        ## wait 2 sec. for the user to correct the fits   ##
        ####################################################
        listen()
        
        ####################################################
        ## then start higher level plotting               ##
        ####################################################
        #det = -na_amp.fitter.X[na_amp.fitter.Ydata.argmax()]
        det = na_amp["delta_hz"]
        #-na_amp.Ydata.argmax()#-min(na_amp["x0_hz"],na_amp["x0_2_hz"])
        #if first:
           # first = False
           # det0 = sp["x0_hz"]
        detuning.appendPoint(sp["x0_hz"],det)
        gamma.appendPoint(sp["gamma_hz"],det)
        #thermoShift.appendPoint(spurious["x0_hz"],det)
        gamma.plot()
        detuning.plot()
        #thermoShift.plot("+",scaleOnMe = False)
        
        
        ####################################################
        ##      plot high level data analysis             ##
        ####################################################
        
       # EITstart = nu_mech - widthEIT/2
        #EITstop  = nu_mech + widthEIT/2
        #nph = calib*(sp["area"])/((na_amp.mean(EITstart-1e6,EITstart)+na_amp.mean(EITstop,EITstop + 1e6))/2)
        
        #import pdb
        #pdb.set_trace()
        nPhonons.appendPoint(nph,det)
        nPhonons.plot()
        
        ####################################################
        ## if autopilot is on,                            ##
        ## check for update of the parameters             ##
        ####################################################
        if autopilot:
            focusOnTrace(sp)
        ####################################################
        ## set Voltage to next value                      ##
        ####################################################
        V = V+step_V
    
def _endOrStop_(self):
    #getAllDVasDefault()
    try:
        gamma.save("gamma",saveInAutoGenDir = True)
        detuning.save("detuning",saveInAutoGenDir = True)
        nPhonons.save("nPhonons",saveInAutoGenDir = True)
    except Exception as e:
        print e
    #thermoShift.save("thermoShift",saveInAutoGenDir = True)
    
    print "press enter"
    yn = raw_input("Should I take Backgrounds? [y]/n")
    if yn != "n":
        takeBackgrounds()
    
    e = defaultDevice("ESA")
    e.write("*RCL 8")

def takeBackgrounds(self):
    print "taking backgrounds..."
    e = defaultDevice("ESA")
    e.write("*RCL 8")
    setV(10,slowly = True)
    
    na = defaultDevice("NA")
    
    e.setRBWAuto()
    e.setSpan(1e6)
    sleep(45)
    e.quickTrace("BG_1MHz",win = "largeSpans")
    
    e.setSpan(10e6)
    sleep(45)
    e.quickTrace("BG_10MHz",win = "largeSpans")
    
    e.setSpan(25e6)
    sleep(45)
    e.quickTrace("BG_25MHz",win = "largeSpans")

    e.write("*rcl 9")
    sleep(45)
    e.quickTrace("BG_wide",win = "largeSpans")

def dummyStuff():
    ####################################################
    ## take a trace of the other mode                 ##
    ## state 7 is used                                ##
    ####################################################
    e.write("*sav 8")
    e.write("*rcl 7")
    sleep(15)
    oth = e.getTrace()
    oth.setName("otherMode_" + theName)
    oth.plot(win = "otherMode",uncheckOthers = True)
    oth.save()







@session
def blinkShutter(_shutterName = "detectorMinus",_time = 0.1):
    other = False
    while(True):
        try:
            setShutter(shutterName,other)
        except KeyError:
            continue
        sleep(time)
        listen()
        other = not other
        
        
@session
def scanLaser(_startV = 0.0,_stopV = 10.0):
    while(True):
        setV(startV,slowly = True)
        listen()
        setV(stopV,slowly = True)
        listen()