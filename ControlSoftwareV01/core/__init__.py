print "init core"

import gc ##let's modify the default behaviour of the garbage collector...
gc.set_threshold(100) #default value is 700, but since we manipulate large objects, better be careful with memory usage



from loadSave import newSessionDir,load,renewTodayDir
from plotting import plot
import utils
import fit
import Spectrum
from utils.Unit import inUnit

from newSession import listen,session


__all__ = ["loadSave","plotting","Spectrum","utils","fit","load","newSessionDir","renewTodayDir","listen","session","inUnit"]




#import plotting
#plotting.GUIon = True
#try:
#    from .. import GUI
#except ValueError as ve:
#    if ve.message == "Attempted relative import beyond toplevel package":
#        plotting.GUIon = False
#    else:
#        Raise(ve)
#else:
#    from ..GUI.Qt_plotManager import plotManager as _pm_
#    plotting.plotManager = _pm_
#    
#import fit
#fit.GUIon = plotting.GUIon