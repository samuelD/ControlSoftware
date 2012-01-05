# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UI_helpWin.ui'
#
# Created: Sun Oct 17 10:54:21 2010
#      by: PyQt4 UI code generator 4.7
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_help(object):
    def setupUi(self, help):
        help.setObjectName("help")
        help.resize(518, 466)
        self.horizontalLayout = QtGui.QHBoxLayout(help)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.textBrowser = QtGui.QTextBrowser(help)
        self.textBrowser.setObjectName("textBrowser")
        self.horizontalLayout.addWidget(self.textBrowser)

        self.retranslateUi(help)
        QtCore.QMetaObject.connectSlotsByName(help)

    def retranslateUi(self, help):
        help.setWindowTitle(QtGui.QApplication.translate("help", "Help", None, QtGui.QApplication.UnicodeUTF8))

