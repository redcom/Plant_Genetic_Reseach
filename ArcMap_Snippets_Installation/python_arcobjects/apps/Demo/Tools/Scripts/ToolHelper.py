# ToolHelper.py
# Updated for ArcGIS 10

def Status(sMsg, pos=-1, gp=None):
    if gp is None:
        print sMsg
    elif pos == -1:
        gp.SetProgressorLabel(sMsg)
    elif pos == 0:
        gp.SetProgressor("step", sMsg)
    else:        
        gp.SetProgressorLabel(sMsg)
        gp.SetProgressorPosition(pos)

def Message(sMsg, gp=None):
    if gp is None:
        print sMsg
    else:
        gp.AddMessage(sMsg)

def Error(sMsg, gp=None):
    if gp is None:
        print "ERROR: " + sMsg
    else:
        gp.AddError(sMsg)

def GetLibPath():
    """Return location of ArcGIS type libraries as string"""
    import _winreg
    keyESRI = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, "SOFTWARE\\ESRI\\Desktop10.0")
    return _winreg.QueryValueEx(keyESRI, "InstallDir")[0] + "com\\"

def NewObj(MyClass, MyInterface):
    """Creates a new comtypes POINTER object where\n\
    MyClass is the class to be instantiated,\n\
    MyInterface is the interface to be assigned"""
    from comtypes.client import CreateObject
    try:
        ptr = CreateObject(MyClass, interface=MyInterface)
        return ptr
    except:
        return None

def CType(obj, interface):
    """Casts obj to interface and returns comtypes POINTER or None"""
    try:
        newobj = obj.QueryInterface(interface)
        return newobj
    except:
        return None
