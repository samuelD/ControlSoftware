from PyQt4 import QtGui,QtCore
from ..core.utils import path
from ..core import utils
import os
#import plotting
from UI_aboutWin import Ui_about
from UI_helpWin import Ui_help
class aboutWin(Ui_about,QtGui.QDialog):#,QtGui.QLabel):
    def __init__(self):#,parent = plotting.plotManager):
        #QtGui.QLabel.__init__(self)
        super(Ui_about,self).__init__()
        self.setupUi(self)
        self.label_2.setText("version "+ utils.version())
        self.image = QtGui.QImage(os.path.join(path.getSourceDir(), "logo.jpg"))
        self.labelImage.setPixmap(QtGui.QPixmap.fromImage(self.image))
#        self.show()
                       

about = aboutWin()


class helpWin(Ui_help,QtGui.QDialog):
    def __init__(self):
        super(Ui_help,self).__init__()
        self.setupUi(self)
        with open(os.path.join(path.getSourceDir(),"help.txt")) as f:
            h = f.read()
        self.textBrowser.setText(h)

help = helpWin()
