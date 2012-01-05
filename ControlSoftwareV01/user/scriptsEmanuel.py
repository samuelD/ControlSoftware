from .. import *
    
    
@session
def readoutScheme(_phi_start = 0.0,_phi_end= 360.0,_phi_incr = 1.0,_avg=100,_nPoints = 1000,_isPlot = True):
    a = defaultDevice("AFG")
    e = defaultDevice("ESA")
               
    

    a.setPhase(90+phi_start)
    a.setChannel(2)
    a.setPhase(phi_start)
    
    e.setAverages(avg)
    e.setPoints(nPoints)
    
    sweTime=e.getSweepTime()
    waitTime=int(toSINumber(avg*sweTime))+1 #wait time before acquiring trace
    
    #a.setChannel(1) # no output for thermal response measurement
    #a.setOutput(False)
    #a.setChannel(2)
    #a.setOutput(False)
    
    #e.restart() # get first Lorentzian trace
    #self.sleep(int(waitTime))
    #sp = e.getTrace()
    #isPlot = self.getDV("isPlot")
    
    #sp.fit(plotAfterwards = isPlot, model = "Lorentz")
    #sp.save("ESA_spectrum")
       
    #a.setChannel(1) # output for feedback response measurement
    #a.setOutput(True)
    #a.setChannel(2)
    #a.setOutput(True)   
       
    phi=0 #phi is phase increment
    
    while a.getPhase()<phi_end:
        "scan phase by 90 deg"
        a.setChannel(1)
        a.setPhase(90+phi_start+phi-80)
        a.setChannel(2)
        a.setPhase(phi_start+phi-80)
        #a.initPhase()
        sleep(1)
        listen()

        e.restart()
        sleep(int(waitTime))
        sp = e.getTrace()
    
        sp.fit(plotAfterwards = isPlot, model = "Lorentz")
        sp.save("ESA_spectrum"+str(phi_start+phi))
        phi = phi+phi_incr
        listen()