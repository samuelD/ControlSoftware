print "init GUI"
from PyQt4 import QtCore,QtGui
import sys
print "launching GUI application"
app = QtCore.QCoreApplication.instance()
if app is None:
    app = QtGui.QApplication(sys.argv)
    



from Qt_plotManager import plotManager
from Qt_dynamicVariables import DVGui


__all__ = ["plotManager","DVGui","app"]

from ..core import flags,fit,newSession


flags.GUIon = True
flags.plotManager = plotManager
flags.app = app
fit.createPanelParams()

from Qt_dynamicVariables import DVGui
newSession.DVGui = DVGui

