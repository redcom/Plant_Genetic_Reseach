# FiveColorTool.py
# Updated for ArcGIS 10

# Set up reporting

import arcpy
from ToolHelper import Status, Error, GetLibPath, NewObj, CType
from comtypes.client import GetModule
bTest = False # Set to True for standalone testing

sLibPath = GetLibPath()
GetModule(sLibPath + "esriSystem.olb")
GetModule(sLibPath + "esriGeometry.olb")
GetModule(sLibPath + "esriGeoDatabase.olb")
GetModule(sLibPath + "esriGeoprocessing.olb")

def DoIt():

    gp = arcpy
    if bTest:
        g = None
    else:
        g = gp
    Status("Initializing...", -1, g)
    import comtypes.gen.esriSystem as esriSystem
    import comtypes.gen.esriGeometry as esriGeometry
    import comtypes.gen.esriGeoDatabase as esriGeoDatabase
    import comtypes.gen.esriGeoprocessing as esriGeoprocessing
    import random

    # Get parameters

    if bTest:
        sInClass = "c:/apps/demo/Temp.gdb/Parcel"
        sColorFieldName = "COLOR"
        sOverlapTolerance = "0.01"
        sAssignRandom = ""
        gp.SetProduct("ArcEditor")
    else:
        sInClass = gp.GetParameterAsText(0)
        sColorFieldName = gp.GetParameterAsText(1)
        sOverlapTolerance = gp.GetParameterAsText(2)
        sAssignRandom = gp.GetParameterAsText(3) # default = False
    dTol = float(sOverlapTolerance)
    bRandomize = (sAssignRandom.lower() == "true")

    # Open feature class

    Status("Opening feature class...", -1, g)
    pGPUtil = NewObj(esriGeoprocessing.GPUtilities, \
                     esriGeoprocessing.IGPUtilities)
    pFC = pGPUtil.OpenFeatureClassFromString(sInClass)
    sShapeName = pFC.ShapeFieldName
    sOIDName = pFC.OIDFieldName
    sSubFields = sOIDName + "," + sShapeName
    iNumRecs = pFC.FeatureCount(None)

    # Set up value list

    Status("Checking color field...", -1, g)
    pTab = CType(pFC, esriGeoDatabase.ITable)
    iColorField = pTab.FindField(sColorFieldName)
    pField = pTab.Fields.Field(iColorField)
    pDomain = pField.Domain
    ValList = []
    iValCount = 5
    if pDomain:
        eType = pDomain.Type
        if eType == esriGeoDatabase.esriDTRange:
            pRangeDomain = CType(pDomain, esriGeoDatabase.IRangeDomain)
            MinVal = pRangeDomain.MinValue
            MaxVal = pRangeDomain.MaxValue
            DeltaVal = (MaxVal - MinVal) / (iValCount - 1)
            for i in range(iValCount):
                ValList.append(MinVal + (i * DeltaVal))
        elif eType == esriGeoDatabase.esriDTCodedValue:
            pCVDomain = CType(pDomain, esriGeoDatabase.ICodedValueDomain)
            iCount = pCVDomain.CodeCount
            if iCount < iValCount:
                sMsg = sColorFieldName + ": too few domain values"
                Error(sMsg, g)
                return
            if bRandomize:
                iValCount = iCount
            for i in range(iValCount):
                ValList.append(pCVDomain.Value(i))
        else:
            sMsg = sColorFieldName + ": unsupported domain type"
            Error(sMsg, g)
            return
    elif pField.Type == esriGeoDatabase.esriFieldTypeString:
        ValList = ["A", "B", "C", "D", "E"]
    else:
        ValList = [0, 1, 2, 3, 4]

    # Build topology

    Status("Building neighbor table...", 0, g)
    NeighborTable = dict()
    pQF = NewObj(esriGeoDatabase.QueryFilter, esriGeoDatabase.IQueryFilter)
    pQF.SubFields = sSubFields
    pSF = NewObj(esriGeoDatabase.SpatialFilter, esriGeoDatabase.ISpatialFilter)
    pSF.GeometryField = sShapeName
    pSF.SubFields = sSubFields
    pSF.SpatialRel = esriGeoDatabase.esriSpatialRelIntersects
    pFCursor = pFC.Search(pQF, True)
    iRecNum = 0
    while True:
        pFeat = pFCursor.NextFeature()
        if not pFeat:
            break
        iRecNum += 1
        if iRecNum % 100 == 0:
            sMsg = "Building neighbor table..." + str(iRecNum)
            iPos = int(iRecNum * 100 / iNumRecs)
            Status(sMsg, iPos, g)
        sOID = str(pFeat.OID)
        pShape = pFeat.Shape
        if not pShape:
            continue
        if pShape.IsEmpty:
            continue
        pPolygon = CType(pShape, esriGeometry.IPolygon)
        if pPolygon.ExteriorRingCount > 1:
            sMsg = "Multipart polygon detected at OID: " + sOID
            Error(sMsg, g)
            return
        pTopoOp = CType(pShape, esriGeometry.ITopologicalOperator)
        pSF.Geometry = pShape
        pSF.WhereClause = sOIDName + " <> " + sOID
        OIDList = []
        pFCursor2 = pFC.Search(pSF, True)
        while True:
            pFeat2 = pFCursor2.NextFeature()
            if not pFeat2:
                break
            pShape2 = pFeat2.Shape
            sOID2 = str(pFeat2.OID)
            # Skip point or multipoint intersection
            pIntShape = pTopoOp.Intersect(pShape2, esriGeometry.esriGeometry0Dimension)
            if not pIntShape.IsEmpty:
                continue
            # Check for polygon overlap
            pIntShape = pTopoOp.Intersect(pShape2, esriGeometry.esriGeometry2Dimension)
            if not pIntShape.IsEmpty:
                pArea = CType(pIntShape, esriGeometry.IArea)
                dArea = pArea.Area
                # If area within tolerance, treat as line intersection
                if dArea <= dTol:
                    OIDList.append(sOID2)
                    continue
                sMsg = "Polygon overlap detected at OID: " + sOID
                sMsg += "\n with OID: " + sOID2
                sMsg += "\nArea = " + str(dArea)
                Error(sMsg, g)
                return
            OIDList.append(sOID2)
        del pFCursor2
        NeighborTable[sOID] = set(OIDList)
    del pFCursor

    # Analyze topology

    Status("Analyzing...", 0, g)
    NodeStack = []
    iLen = len(NeighborTable)
    iRecNum = 0
    while iLen > 0:
        
        iRecNum += 1
        if iRecNum % 1000 == 0:
            sMsg = "Analyzing..." + str(iRecNum)
            iPos = int(iRecNum * 100 / iNumRecs)
            Status(sMsg, iPos, g)

        # Search for Rule 1:
        # If X has fewer than 5 neighbors,
        # add X to the node stack and remove it from the topology

        bFound = False
        for sOID, OIDSet in NeighborTable.iteritems():
            if len(OIDSet) > 4:
                continue
            NodeStack.append([sOID, OIDSet])
            for sOID2 in OIDSet:
                OIDSet2 = NeighborTable[sOID2]
                OIDSet2.remove(sOID)
            del NeighborTable[sOID]
            bFound = True
            break
        if bFound:
            iLen = len(NeighborTable) # iLen -= 1
            continue

        # If no entries match rule 1, search for Rule 2:
        # If X has five neighbors, two of which have at most
        # at most seven neighbors and are not neighbors of each other,
        # add X to the node stack, remove it from the topology,
        # and combine the two neighbors into a single node connected
        # their neighbors plus X's remaining neighbors

        bFound = False
        for sOID, OIDSet in NeighborTable.iteritems():
            iCount = len(OIDSet)
            if iCount != 5:
                continue
            bFound = False
            OIDList = list(OIDSet)
            for i in range(iCount - 1):
                sOID2 = OIDList[i]
                OIDSet2 = NeighborTable[sOID2]
                if len(OIDSet2) > 7:
                    continue
                for j in range(i + 1, iCount):
                    sOID3 = OIDList[j]
                    if sOID3 in OIDSet2:
                        continue
                    OIDSet3 = NeighborTable[sOID3]
                    if len(OIDSet3) > 7:
                        continue
                    bFound = True
                    break
                if bFound:
                    break
            if not bFound:
                continue
            NodeStack.append([sOID, OIDSet])
            sN1 = sOID2
            sN2 = sOID3
            sNewOID = sN1 + "/" + sN2
            NewOIDSet = OIDSet | OIDSet2 | OIDSet3
            NewOIDSet.remove(sOID)
            NewOIDSet.remove(sN1)
            NewOIDSet.remove(sN2)
            del NeighborTable[sOID]
            del NeighborTable[sN1]
            del NeighborTable[sN2]
            for sOID2 in NewOIDSet:
                OIDSet2 = NeighborTable[sOID2]
                if sOID in OIDSet2:
                    OIDSet2.remove(sOID)
                if sN1 in OIDSet2:
                    OIDSet2.remove(sN1)
                if sN2 in OIDSet2:
                    OIDSet2.remove(sN2)
                OIDSet2.add(sNewOID)
            NeighborTable[sNewOID] = NewOIDSet
            break                
        if bFound:
            iLen = len(NeighborTable) # iLen -= 2
            continue
        # This should never happen
        # (if the overlap tolerance isn't too large)
        Error("Could not apply rule 2 at OID: " + sOID, g)
        del NeighborTable
        del NodeStack
        return

    # Build color table

    Status("Building color table...", 0, g)
    ColorTable = dict()
    iLen = len(NodeStack)
    iRecNum = 0
    while iLen > 0:

        iRecNum += 1
        if iRecNum % 1000 == 0:
            sMsg = "Building color table..." + str(iRecNum)
            iPos = int(iRecNum * 100 / iNumRecs)
            Status(sMsg, iPos, g)

        NodeEntry = NodeStack.pop()
        sOID = NodeEntry[0]
        OIDSet = NodeEntry[1]
        ColorList = []
        for i in range(iValCount):
            ColorList.append(False)
        for sOID2 in OIDSet:
            sOID3 = sOID2.split("/")[0]
            if not sOID3 in ColorTable:
                continue
            i = ColorTable[sOID3]
            ColorList[i] = True
        Available = []
        for i in range(len(ColorList)):
            if ColorList[i]:
                continue
            Available.append(i)
        iCount = len(Available)
        if iCount == 0:
            # This should never happen
            # (unless the overlap tolerance is too large)
            sMsg = "Could not assign color at OID: " + sOID
            Error(sMsg, g)
            del NodeStack
            del ColorTable
            return
        if bRandomize:
            i = random.randint(0, iCount - 1)
        else:
            i = 0
        iColor = Available[i]            
        for sOID2 in sOID.split("/"):
            ColorTable[sOID2] = iColor
        iLen -= 1

    # Calculate color field

    Status("Calculating color field...", 0, g)
    pQF.SubFields = sOIDName + "," + sColorFieldName
    pCursor = pTab.Update(pQF, False)
    iRecNum = 0
    while True:
        pRow = pCursor.NextRow()
        if not pRow:
            break
        iRecNum += 1
        if iRecNum % 1000 == 0:
            sMsg = "Calculating color field..." + str(iRecNum)
            iPos = int(iRecNum * 100 / iNumRecs)
            Status(sMsg, iPos, g)
        iOID = pRow.OID
        iColor = ColorTable[str(iOID)]
        pRow.Value[iColorField] = ValList[iColor]
        pCursor.UpdateRow(pRow)
    del pCursor
    del ColorTable
    del pTab
    del pFC
    Status("Done.", 0, g)

if __name__ == "__main__":
    DoIt()
