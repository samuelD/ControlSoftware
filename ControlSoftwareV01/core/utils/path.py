import os

def version():
    return getSourceDir()[-2:]




def getSourceDir():
    sourceDir = os.path.dirname(__file__)
    if sourceDir == "":
        sourceDir = os.path.abspath("")
    return os.path.abspath(os.path.join(sourceDir,"..",".."))
def getPathFile():
    return os.path.join(getConfDir(),"path.cfg")


def getUserDir():
    return os.path.join(getSourceDir(),"user")


def getIconDir():
    return os.path.join(getSourceDir(),"icons")

def getPlotDefaultDir():
    return os.path.join(getSourceDir(),"plotDefaults")

def getFitDefaultDir():
    return os.path.join(getSourceDir(),"fitDefaults")

def getConfDir():
    return os.path.join(getSourceDir(),"conf")

def getHardwareFile():
    return os.path.join(getConfDir(),"hardware.cfg")

def getSessionDir():
    return os.path.join(getConfDir(),"defaultSessions")


if not os.path.exists(getConfDir()):
    os.mkdir(getConfDir())   


if not os.path.exists(getSessionDir()):
    os.mkdir(getSessionDir())   