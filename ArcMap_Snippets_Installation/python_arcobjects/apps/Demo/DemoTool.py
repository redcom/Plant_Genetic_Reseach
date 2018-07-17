# DemoTool.py

#**** Initialization ****

import _winreg
import math
import os
import random
import sys
import traceback
import zipfile
import ctypes
import comtypes
import comtypes.server.localserver

from Snippets import GetLibPath, NewObj, CType, CLSID, Msg
from comtypes.client import GetModule
sLibPath = GetLibPath();
GetModule(sLibPath + "esriFramework.olb")
GetModule(sLibPath + "esriArcMapUI.olb")
GetModule("DemoTool.tlb")
from comtypes.gen.DemoToolLib import MyTool

sCATID_MxCommands = "{B56A7C42-83D4-11D2-A2E9-080009B6F22B}" # CATID_MxCommands (from ArcCATIDs.h)
ICONPATH = "C:\\apps\\Demo\\icons\\"
QuoteList = ["Oh, intercourse the penguin!", \
             "Why did you say Burma?", \
             "It's not pining, it's passed on.", \
             "THAT'S got Spam in it!", \
             "If we took the bones out it wouldn't be crunchy would it?", \
             "It's being-hit-on-the-head lessons in here.", \
             "In that case, give me a bee license.", \
             "It's a bit runny.", \
             "I'm afraid what you've got hold of there is an anteater.", \
             "What's wrong with fruit?", \
             "Fetch... THE COMFY CHAIR!", \
             "He was a hard man. Vicious but fair.", \
             "Mr Neutron is missing, sir!", \
             "I happen to know that this is the Lupin Express.", \
             "There is no cannibalism in the British Navy.", \
             "Oh Fred, I think we've got an eater."]

#**** Helper Functions ****

def GetESRIConfigDir():
    sDir = "C:\\Program Files\\Common Files\\ArcGIS\\Desktop10.0\\Configuration\\CATID"
    return sDir
    
def GetESRIConfigFileName():
    sArc10ConfigDir = GetESRIConfigDir()
    sDemoToolLib_UUID = "{27722EEC-E805-4CE7-9239-45072B25D8C7}" # from DemoTool.idl
    sLibName = "DemoToolLib" # also from DemoTool.idl
    sName = sArc10ConfigDir + "\\" + sDemoToolLib_UUID.lower()
    sName += "_" + sLibName.lower() + ".ecfg"
    return sName

def RegisterCategory():
    # Create config.xml
    sXMLName = os.environ["TEMP"] + "\\config.xml"
    sMyUUID = CLSID(MyTool)
    sFileName = "c:\\apps\\Demo\\DemoTool\\DemoTool.tlb"
    sLine = '<?xml version="1.0"?>\n'
    sLine += '<ESRI.Configuration ver="1" FileName="' + sFileName + '">'
    sLine += '<Categories><Category CATID="' + sCATID_MxCommands + '">'
    sLine += '<Class CLSID="' + sMyUUID + '"/>'
    sLine += '</Category></Categories></ESRI.Configuration>\n'
    f = open(sXMLName, "w")
    f.write(sLine)
    f.flush()
    f.close()
    # Check if config dir exists
    sArc10ConfigDir = GetESRIConfigDir()
    if not os.path.exists(sArc10ConfigDir):
        os.makedirs(sArc10ConfigDir)
    # Create ecfg (zip) file
    sECFGName = GetESRIConfigFileName()
    z = zipfile.ZipFile(sECFGName, "w", zipfile.ZIP_DEFLATED)
    z.write(sXMLName, "config.xml")
    z.close()
    os.remove(sXMLName)
    return

def UnregisterCategory():
    sECFGName = GetESRIConfigFileName()
    if os.path.exists(sECFGName):
        os.remove(sECFGName)
    return

def LoadImage(sFilePath, bBitmap):
    from ctypes import c_int, WINFUNCTYPE, windll
    from ctypes.wintypes import HANDLE, LPCSTR, UINT, HINSTANCE
    prototype = WINFUNCTYPE(HANDLE, HINSTANCE, LPCSTR, UINT, c_int, c_int, UINT)
    paramflags = (1, "hinst", 0), (1, "Name", ""), (1, "Type", 0), \
                 (1, "xDesired", 0), (1, "yDesired", 0), (1, "Load", 0)
    fn = prototype(("LoadImageA", windll.user32), paramflags)
    IMAGE_BITMAP = 0
    IMAGE_CURSOR = 2
    LR_LOADFROMFILE = 16
    if bBitmap:
        Option = IMAGE_BITMAP
    else:
        Option = IMAGE_CURSOR
    return fn(Name=sFilePath, Type=Option, Load=LR_LOADFROMFILE)

def RandomQuote():
    iCount = len(QuoteList)
    i = random.randint(0, iCount - 1)
    return QuoteList[i]

#**** MyTool Class Definition ****

class MyToolImpl(MyTool):
    # registry entries
    _reg_threading_ = "Both"
    _reg_progid_ = "DemoToolLib.MyTool.1"
    _reg_novers_progid_ = "DemoToolLib.MyTool"
    _reg_desc_ = "DemoToolLib.MyTool"
    _reg_clsctx_ = comtypes.CLSCTX_INPROC_SERVER | comtypes.CLSCTX_LOCAL_SERVER
    _regcls_ = comtypes.server.localserver.REGCLS_MULTIPLEUSE
    # member variables
    def __init__(self):
        self.m_bitmap = None
        self.m_cursor = None
        self.m_pApp = None
        self.m_pDoc = None
    # IMyTool implementation
    def MyMethod(self, a, b):
        return a + b
    # ICommand implementation
    @property
    def Name(self):
        return "Python_MyTool"
    @property
    def Category(self):
        return "Python"
    @property
    def Caption(self):
        return "MyTool"
    @property
    def Tooltip(self):
        return "Random Quote"
    @property
    def Message(self):
        return "Click on map to add random quote"
    @property
    def Bitmap(self):
        if not self.m_bitmap:
            sPath = ICONPATH + "MyTool.bmp"
            self.m_bitmap = LoadImage(sPath, True)
        return self.m_bitmap
    @property
    def Enabled(self):
        import comtypes.gen.esriCarto as esriCarto
        if not self.m_pDoc:
            return False
        pAV = self.m_pDoc.ActiveView
        if not CType(pAV, esriCarto.IMap):
            return False
        return True
    def OnCreate(self, hook):
        import comtypes.gen.esriFramework as esriFramework
        import comtypes.gen.esriArcMapUI as esriArcMapUI
        self.m_pApp = CType(hook, esriFramework.IApplication)
        pDoc = self.m_pApp.Document
        self.m_pDoc = CType(pDoc, esriArcMapUI.IMxDocument)
        return
    def OnClick(self):
        return
    # ITool implementation    
    @property
    def Cursor(self):
        if not self.m_cursor:
            sPath = ICONPATH + "MyTool.cur"
            self.m_cursor = LoadImage(sPath, False)
        return self.m_cursor
    def OnMouseDown(self, button, shift, x, y):
        import comtypes.gen.esriDisplay as esriDisplay
        import comtypes.gen.esriGeometry as esriGeometry
        import comtypes.gen.stdole as stdole
        import comtypes.gen.esriCarto as esriCarto
        # Get screen display
        pMap = self.m_pDoc.FocusMap
        pAV = CType(pMap, esriCarto.IActiveView)
        pSD = pAV.ScreenDisplay
        # Get point and angle
        try:
            pRubberBand = NewObj(esriDisplay.RubberLine, esriDisplay.IRubberBand)
            pGeom = pRubberBand.TrackNew(pSD, None)
            pSC = CType(pGeom, esriGeometry.ISegmentCollection)
            pLine = CType(pSC.Segment(0), esriGeometry.ILine)
            pPoint = pLine.FromPoint
            dAngle = math.degrees(pLine.Angle)
        except:
            sMsg = "Error getting geometry\n" + traceback.format_exc()
            Msg(sMsg)
            return
        # Create text symbol
        pColor = NewObj(esriDisplay.RgbColor, esriDisplay.IRgbColor)
        pColor.Red = 255
        pFontDisp = NewObj(stdole.StdFont, stdole.IFontDisp)
        pFontDisp.Name = "Arial"
        pFontDisp.Bold = True
        pTextSymbol = NewObj(esriDisplay.TextSymbol, esriDisplay.ITextSymbol)
        pTextSymbol.Font = pFontDisp
        pTextSymbol.Color = pColor
        pTextSymbol.Size = 12
        pTextSymbol.Angle = dAngle
        pTextBackground = NewObj(CLSID(esriDisplay.BalloonCallout), esriDisplay.ITextBackground)
        pFormattedTS = CType(pTextSymbol, esriDisplay.IFormattedTextSymbol)
        pFormattedTS.Background = pTextBackground
        # Create text element and add it to map
        pTextElement = NewObj(esriCarto.TextElement, esriCarto.ITextElement)
        pTextElement.Symbol = pTextSymbol
        pTextElement.Text = RandomQuote()
        pElement = CType(pTextElement, esriCarto.IElement)
        pElement.Geometry = pPoint
        pGC = CType(pMap, esriCarto.IGraphicsContainer)
        pGC.AddElement(pElement, 0)
        pGCSel = CType(pMap, esriCarto.IGraphicsContainerSelect)
        pGCSel.SelectElement(pElement)
        iOpt = esriCarto.esriViewGraphics + \
               esriCarto.esriViewGraphicSelection
        pAV.PartialRefresh(iOpt, None, None)
        return
    def Deactivate(self):
        return True

#**** Registration ****

if __name__ == "__main__":
    from comtypes.server.register import UseCommandLine
    sArg = ""
    if len(sys.argv) > 1:
        sArg = sys.argv[1]
    if sArg == "/unregserver" or sArg == "-unregserver":
        UnregisterCategory()
    UseCommandLine(MyToolImpl)
    if sArg == "/regserver" or sArg == "-regserver":
        RegisterCategory()
