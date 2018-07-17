# RandomColors.py
# Updated for ArcGIS 10

def DoIt():

    # Initialize gp and get parameters

    import arcpy
    import random

    gp = arcpy
    sInTable = gp.GetParameterAsText(0)
    sField = gp.GetParameterAsText(1)
    sOverwrite = gp.GetParameterAsText(2).lower()
    bOverwrite = (sOverwrite == "true")

    ColorList = ["blue", "brown", "cyan", "green", "grey", "magenta", \
                 "orange", "red", "yellow"]
    iCount = len(ColorList)

    # Open update cursor and loop through rows

    iUpdated = 0
    rows = gp.UpdateCursor(sInTable, "", "", sField)
    while True:
        row = rows.next()
        if not row:
            break
        if not bOverwrite:
            val = row.getValue(sField)
            if not (val == "" or val == None):
                continue
        i = random.randint(0, iCount - 1)
        row.setValue(sField, ColorList[i])
        rows.updateRow(row)
        iUpdated += 1
    del row
    del rows
    gp.AddMessage("Rows updated: " + str(iUpdated))

if __name__ == "__main__":
    DoIt()
