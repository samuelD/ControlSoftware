# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UI_plotManager.ui'
#
# Created: Sun Oct 17 10:53:20 2010
#      by: PyQt4 UI code generator 4.7
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.treeWidget = QtGui.QTreeWidget(self.centralwidget)
        self.treeWidget.setGeometry(QtCore.QRect(0, 0, 801, 551))
        self.treeWidget.setIndentation(20)
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.header().setDefaultSectionSize(300)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuAbout = QtGui.QMenu(self.menubar)
        self.menuAbout.setObjectName("menuAbout")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionLoad = QtGui.QAction(MainWindow)
        self.actionLoad.setObjectName("actionLoad")
        self.actionLoad_multiple = QtGui.QAction(MainWindow)
        self.actionLoad_multiple.setObjectName("actionLoad_multiple")
        self.actionLoad_dir = QtGui.QAction(MainWindow)
        self.actionLoad_dir.setObjectName("actionLoad_dir")
        self.actionKill_all_windows = QtGui.QAction(MainWindow)
        self.actionKill_all_windows.setObjectName("actionKill_all_windows")
        self.actionProgram_version = QtGui.QAction(MainWindow)
        self.actionProgram_version.setObjectName("actionProgram_version")
        self.actionCredits = QtGui.QAction(MainWindow)
        self.actionCredits.setObjectName("actionCredits")
        self.actionBugs_comments = QtGui.QAction(MainWindow)
        self.actionBugs_comments.setObjectName("actionBugs_comments")
        self.actionHelp = QtGui.QAction(MainWindow)
        self.actionHelp.setObjectName("actionHelp")
        self.actionAbout_He3Control = QtGui.QAction(MainWindow)
        self.actionAbout_He3Control.setObjectName("actionAbout_He3Control")
        self.actionBugs = QtGui.QAction(MainWindow)
        self.actionBugs.setObjectName("actionBugs")
        self.menuFile.addAction(self.actionLoad)
        self.menuFile.addAction(self.actionLoad_multiple)
        self.menuFile.addAction(self.actionLoad_dir)
        self.menuFile.addAction(self.actionKill_all_windows)
        self.menuAbout.addAction(self.actionHelp)
        self.menuAbout.addAction(self.actionBugs)
        self.menuAbout.addSeparator()
        self.menuAbout.addAction(self.actionAbout_He3Control)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuAbout.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "plotManager", None, QtGui.QApplication.UnicodeUTF8))
        self.treeWidget.headerItem().setText(0, QtGui.QApplication.translate("MainWindow", "win/curve", None, QtGui.QApplication.UnicodeUTF8))
        self.treeWidget.headerItem().setText(1, QtGui.QApplication.translate("MainWindow", "date", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFile.setTitle(QtGui.QApplication.translate("MainWindow", "file", None, QtGui.QApplication.UnicodeUTF8))
        self.menuAbout.setTitle(QtGui.QApplication.translate("MainWindow", "help", None, QtGui.QApplication.UnicodeUTF8))
        self.actionLoad.setText(QtGui.QApplication.translate("MainWindow", "load...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionLoad_multiple.setText(QtGui.QApplication.translate("MainWindow", "load multiple...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionLoad_dir.setText(QtGui.QApplication.translate("MainWindow", "load dir...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionKill_all_windows.setText(QtGui.QApplication.translate("MainWindow", "kill all windows!", None, QtGui.QApplication.UnicodeUTF8))
        self.actionProgram_version.setText(QtGui.QApplication.translate("MainWindow", "program version", None, QtGui.QApplication.UnicodeUTF8))
        self.actionCredits.setText(QtGui.QApplication.translate("MainWindow", "credits", None, QtGui.QApplication.UnicodeUTF8))
        self.actionBugs_comments.setText(QtGui.QApplication.translate("MainWindow", "bugs + comments", None, QtGui.QApplication.UnicodeUTF8))
        self.actionHelp.setText(QtGui.QApplication.translate("MainWindow", "help...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAbout_He3Control.setText(QtGui.QApplication.translate("MainWindow", "about He3Control...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionBugs.setText(QtGui.QApplication.translate("MainWindow", "bugs/suggestions", None, QtGui.QApplication.UnicodeUTF8))

