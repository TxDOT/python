#March 2014
#Adam Breznicky, TxDOT TPP - Mapping Group
#
#This script is designed to be used as a 'tool' within an ArcGIS Toolbox and run within an MXD.
#
# It requires only a single parameter input.
#When working within an MXD, the parameter required is the 'layer' with a selection which you wish to create a query
#to identify.
#
#The result is a .txt file, saved on the users desktop, and 'popped' open for immediate use.
#
#

import arcpy, os


def createsqlquery():
    wksp = os.path.expanduser("~\\Desktop\\")
    arcpy.env.overwriteOutput = True

    fc = arcpy.GetParameterAsText(0)

    fields = arcpy.ListFields(fc)
    for field in fields:
        if field.name == "FID":
            identifier = "FID"
        elif field.name == "OBJECTID":
            identifier = "OBJECTID"


    txtFile = open(wksp + fc + "_SQLquery1.txt", "w")
    txtFile.write("\"" + identifier + "\" in (")


    cursor = arcpy.SearchCursor(fc)


    counter = 0
    for row in cursor:
        thisID = row.getValue(identifier)
        print str(thisID)
        if counter == 0:
            txtFile.write(str(thisID))
            counter += 1
        else:
            txtFile.write(", " + str(thisID))

    del cursor

    txtFile.write(")")
    os.startfile(wksp + fc + "_SQLquery1.txt")
    print "Script Complete"

createsqlquery()
