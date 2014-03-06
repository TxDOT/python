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
