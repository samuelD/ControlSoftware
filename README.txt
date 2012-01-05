The following steps should be followed to have an operational version of the package:

0) Uninstall your previous Python distribution (e.g. pythonXY)

1) Download and install the lattest version of enthought python:
http://www.enthought.com/

2) install the lattest version of PyQt from 
http://www.riverbankcomputing.co.uk/software/pyqt/download
scroll down to find the windows installer...
CAREFULL INSTALL FOR PYTHON 2.7 (32 or 64 bits depending on your system)

4) Install Pyvisa if you wish to control devices: http://sourceforge.net/projects/pyvisa/files/PyVISA/

3) I strongly advise to install ECLIPSE (http://www.eclipse.org/downloads/)
- Then you should add the PyDev plugin (http://pydev.org/manual_101_install.html)

4) with a normal MS DOS console, go to this directory and type: python setup.py install
- This will ask you if you want to install unum (enter y if you don t have it already installed)
- This will also ask you for the default load and save directories to fill the corresponding local config files
- This will finaly detect hardware connected to your computer and fill the corresponding config file

5) To use the program, open an IPython console with the option --pylab=qt 
(for instance in a MS DOS console, type: ipyhon qtconsole --pylab=qt)
then you can cd to the trunk directory and type from He3ControlV?? import *
At this point you should consider edit the local variable PYTHONPATH to add the trunk folder, such that the package is directly accessible
