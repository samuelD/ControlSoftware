# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\He3Control\trunk\He3ControlV08\GUI\UI_dynamicVariables.ui'
#
# Created: Wed Nov 09 17:22:42 2011
#      by: PyQt4 UI code generator 4.8.5
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(514, 298)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Dialog.sizePolicy().hasHeightForWidth())
        Dialog.setSizePolicy(sizePolicy)
        Dialog.setWindowTitle(QtGui.QApplication.translate("Dialog", "sessions", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox = QtGui.QGroupBox(Dialog)
        self.groupBox.setGeometry(QtCore.QRect(10, 79, 501, 80))
        self.groupBox.setTitle(QtGui.QApplication.translate("Dialog", "session control", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setFlat(False)
        self.groupBox.setCheckable(False)
        self.groupBox.setChecked(False)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.buttonDebug = QtGui.QPushButton(self.groupBox)
        self.buttonDebug.setGeometry(QtCore.QRect(250, 20, 75, 23))
        self.buttonDebug.setText(QtGui.QApplication.translate("Dialog", "DEBUG", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonDebug.setObjectName(_fromUtf8("buttonDebug"))
        self.buttonPause = QtGui.QPushButton(self.groupBox)
        self.buttonPause.setGeometry(QtCore.QRect(170, 20, 75, 23))
        self.buttonPause.setText(QtGui.QApplication.translate("Dialog", "PAUSE", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonPause.setObjectName(_fromUtf8("buttonPause"))
        self.buttonStop = QtGui.QPushButton(self.groupBox)
        self.buttonStop.setGeometry(QtCore.QRect(90, 20, 75, 23))
        self.buttonStop.setText(QtGui.QApplication.translate("Dialog", "STOP", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonStop.setObjectName(_fromUtf8("buttonStop"))
        self.labelExplanation = QtGui.QLabel(self.groupBox)
        self.labelExplanation.setGeometry(QtCore.QRect(20, 50, 421, 16))
        self.labelExplanation.setText(QtGui.QApplication.translate("Dialog", "no session running", None, QtGui.QApplication.UnicodeUTF8))
        self.labelExplanation.setObjectName(_fromUtf8("labelExplanation"))
        self.labelStatus = QtGui.QLabel(self.groupBox)
        self.labelStatus.setGeometry(QtCore.QRect(20, 25, 46, 13))
        self.labelStatus.setText(QtGui.QApplication.translate("Dialog", "Stopped", None, QtGui.QApplication.UnicodeUTF8))
        self.labelStatus.setObjectName(_fromUtf8("labelStatus"))
        self.checkBox = QtGui.QCheckBox(self.groupBox)
        self.checkBox.setGeometry(QtCore.QRect(390, 20, 101, 17))
        self.checkBox.setText(QtGui.QApplication.translate("Dialog", "newSessionDir", None, QtGui.QApplication.UnicodeUTF8))
        self.checkBox.setObjectName(_fromUtf8("checkBox"))
        self.groupBox_2 = QtGui.QGroupBox(Dialog)
        self.groupBox_2.setGeometry(QtCore.QRect(10, 0, 501, 81))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("Dialog", "save directory", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.buttonBrowse = QtGui.QPushButton(self.groupBox_2)
        self.buttonBrowse.setGeometry(QtCore.QRect(0, 18, 31, 23))
        self.buttonBrowse.setText(QtGui.QApplication.translate("Dialog", "(...)", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonBrowse.setObjectName(_fromUtf8("buttonBrowse"))
        self.buttonCreate = QtGui.QPushButton(self.groupBox_2)
        self.buttonCreate.setGeometry(QtCore.QRect(440, 19, 41, 23))
        self.buttonCreate.setText(QtGui.QApplication.translate("Dialog", "create", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonCreate.setObjectName(_fromUtf8("buttonCreate"))
        self.labelLastSaved = QtGui.QLabel(self.groupBox_2)
        self.labelLastSaved.setGeometry(QtCore.QRect(76, 51, 421, 20))
        self.labelLastSaved.setText(QtGui.QApplication.translate("Dialog", "M:/Samples/wafer11/toroid8/003_mode1_cal_5mV", None, QtGui.QApplication.UnicodeUTF8))
        self.labelLastSaved.setObjectName(_fromUtf8("labelLastSaved"))
        self.lineSessionName = QtGui.QLineEdit(self.groupBox_2)
        self.lineSessionName.setGeometry(QtCore.QRect(314, 20, 111, 20))
        self.lineSessionName.setText(QtGui.QApplication.translate("Dialog", "toroid8", None, QtGui.QApplication.UnicodeUTF8))
        self.lineSessionName.setObjectName(_fromUtf8("lineSessionName"))
        self.labelSaveDir = QtGui.QLabel(self.groupBox_2)
        self.labelSaveDir.setGeometry(QtCore.QRect(40, 20, 271, 20))
        self.labelSaveDir.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.labelSaveDir.setText(QtGui.QApplication.translate("Dialog", "\"today directory\"", None, QtGui.QApplication.UnicodeUTF8))
        self.labelSaveDir.setObjectName(_fromUtf8("labelSaveDir"))
        self.label_6 = QtGui.QLabel(self.groupBox_2)
        self.label_6.setGeometry(QtCore.QRect(10, 50, 61, 20))
        self.label_6.setText(QtGui.QApplication.translate("Dialog", "last saved :", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setObjectName(_fromUtf8("label_6"))

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        pass

