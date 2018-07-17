# EliminateOverlaps.py
# Updated for ArcGIS 10

# Set up reporting

import arcpy
from ToolHelper import Status, Message, GetLibPath, NewObj, CType
from comtypes.client import GetModule
bTest = False # Set to True for standalone testing

sLibPath = GetLibPath()
GetModule(sLibPath + "esriSystem.olb")
GetModule(sLibPath + "esriGeometry.olb")
GetModule(sLibPath + "esriGeoDatabase.olb")
GetModule(sLibPath + "esriGeoprocessing.olb")

# Helper functions

def RemoveSlivers(pShape, dTol):
    import comtypes.gen.esriGeometry as esriGeometry
    if pShape.IsEmpty:
        return False
    pGC = CType(pShape, esriGeometry.IGeometryCollection)
    iGeomCount = pGC.GeometryCount
    bSlivers = False
    for i in range (iGeomCount):
        j = iGeomCount - 1 - i
        pPart = pGC.Geometry(j)
        pPartArea = CType(pPart, esriGeometry.IArea)
        dArea = abs(pPartArea.Area)
        if dArea > dTol:
            continue
        pGC.RemoveGeometries(j, 1)
        bSlivers = True
    if not bSlivers:
        return False
    pTopoOp = CType(pShape, esriGeometry.ITopologicalOperator)
    pTopoOp.Simplify()
    return True

# Do it

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

    # Get parameters

    if bTest:
        sInClass = "c:/apps/demo/temp.gdb/Tax_Area_In"
        sOutClass = "c:/apps/demo/temp.gdb/Tax_Area_Out"
        sMaxSliverArea = "20"
        gp.SetProduct("ArcEditor")
    else:
        sInClass = gp.GetParameterAsText(0)
        sOutClass = gp.GetParameterAsText(1)
        sMaxSliverArea = gp.GetParameterAsText(2)
    dSliverTol = float(sMaxSliverArea)

    # Copy feature class

    Status("Copying feature class...", -1, g)
    gp.Copy_management(sInClass, sOutClass)

    # Repair geometry

    Status("Repairing geometry...", -1, g)
    gp.RepairGeometry_management(sOutClass)

    # Open feature class

    Status("Opening feature class...", -1, g)
    pGPUtil = NewObj(esriGeoprocessing.GPUtilities, esriGeoprocessing.IGPUtilities)
    pFC = pGPUtil.OpenFeatureClassFromString(sOutClass)
    sShapeName = pFC.ShapeFieldName
    sOIDName = pFC.OIDFieldName
    sSubFields = sOIDName + "," + sShapeName
    iNumRecs = pFC.FeatureCount(None)

    # Loop through records

    Status("Eliminating overlaps...", 0, g)
    pSF = NewObj(esriGeoDatabase.SpatialFilter, esriGeoDatabase.ISpatialFilter)
    pSF.GeometryField = sShapeName
    pSF.SubFields = sSubFields
    # (esriSpatialRelOverlaps fails if two polygons are identical)
    pSF.SpatialRel = esriGeoDatabase.esriSpatialRelIntersects
    # !!!! Do NOT assign subfields to an update cursor - script go boom !!!!
    pFCursor = pFC.Update(None, False)
    iRecNum = 0
    iUpdated = 0
    iDeleted = 0
    while True:

        # Get shape

        pFeat = pFCursor.NextFeature()
        if not pFeat:
            break
        iRecNum += 1
        if iRecNum % 100 == 0:
            sMsg = "Eliminating overlaps..." + str(iRecNum)
            iPos = int(iRecNum * 100 / iNumRecs)
            Status(sMsg, iPos, g)
        sOID = str(pFeat.OID)
        pShape = pFeat.ShapeCopy
        if not pShape:
            # This should never happen
            pFCursor.DeleteFeature()
            iDeleted += 1
            continue
        if pShape.IsEmpty:
            # This should never happen
            pFCursor.DeleteFeature()
            iDeleted += 1
            continue
        bUpdated = RemoveSlivers(pShape, dSliverTol)
        if pShape.IsEmpty:
            pFCursor.DeleteFeature()
            iDeleted += 1
            continue
        pTopoOp = CType(pShape, esriGeometry.ITopologicalOperator)
        pArea = CType(pShape, esriGeometry.IArea)
        dArea = pArea.Area

        # Get intersecting polygons
        
        bEmpty = False
        pSF.Geometry = pShape
        pSF.WhereClause = sOIDName + " <> " + sOID
        pFCursor2 = pFC.Search(pSF, True)
        pNewShape = None
        while True:
            pFeat2 = pFCursor2.NextFeature()
            if not pFeat2:
                break
            pShape2 = pFeat2.ShapeCopy
            sOID2 = str(pFeat2.OID)
            bResult = RemoveSlivers(pShape2, dSliverTol)
            if pShape2.IsEmpty:
                continue
            # Skip if no polygon overlap
            pIntShape = pTopoOp.Intersect(pShape2, esriGeometry.esriGeometry2Dimension)
            if pIntShape.IsEmpty:
                continue
            # Skip if other polygon is larger
            pArea2 = CType(pShape2, esriGeometry.IArea)
            dArea2 = pArea2.Area
            if dArea < dArea2:
                continue
            # Subtract adjacent polygon
            bUpdated = True
            pNewShape = pTopoOp.Difference(pShape2)
            bResult = RemoveSlivers(pNewShape, dSliverTol)
            bEmpty = pNewShape.IsEmpty
            if bEmpty:
                del pFeat2
                break
            pTopoOp = CType(pNewShape, esriGeometry.ITopologicalOperator)
            pArea = CType(pNewShape, esriGeometry.IArea)
            dArea = pArea.Area
        del pFCursor2
        if not bUpdated:
            continue
        if bEmpty:
            pFCursor.DeleteFeature()
            iDeleted += 1
            continue
        pFeat.Shape = pNewShape
        pFCursor.UpdateFeature(pFeat)
        iUpdated += 1

    del pFCursor
    del pFC

    sMsg = "Records updated: " + str(iUpdated)
    sMsg += "\nRecords deleted: " + str(iDeleted)
    Message(sMsg, g)

if __name__ == "__main__":
    DoIt()
