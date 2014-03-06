__file__ = 'AdminPrefix_Resourcer_v1'
__date__ = '3/5/14'
__author__ = 'ABREZNIC'
#
#after designating the 'directory' variable, this script, when run, will walk through each folder and subfolder and file
#and identify the MXDs. For each MXD, the script will re-source the layers which have a Comanche feature class
#that has been updated with the new 'Admin' prefix/account
#


#import modules
import arcpy, os

#variables
directory = "C:\\TxDOT\\Scratch\\replace_sourceMXD"

#issue list
issues = []

#walk through each directory
for root, dirs, files in os.walk(directory):
    #ignore file and personal geodatabases
    specDir = root.split("\\")[-1]
    dbsuffix = specDir.split(".")[-1]
    if dbsuffix == "gdb" or dbsuffix == "mdb" or dbsuffix == "tbx":
        pass
    else:
        for n in files:
            #identify the mxds
            if str(n).split(".")[-1] == "mxd":
                print "working on: " + str(os.path.join(root, n))
                map = arcpy.mapping.MapDocument(os.path.join(root, n))
                dataframes = arcpy.mapping.ListDataFrames(map)
                for df in dataframes:
                    layers = arcpy.mapping.ListLayers(map, "", df)
                    for lyr in layers:
                        try:
                            if "TPP_GIS.MCHAMB1." in lyr.dataSource:
                                print "lyr source: " + lyr.dataSource
                                newsource = lyr.dataSource.replace("TPP_GIS.MCHAMB1.", "TPP_GIS.APP_TPP_GIS_ADMIN.")
                                location = newsource.split("\\")[:-2]
                                locationFixed = "\\".join(location)
                                print locationFixed
                                newname = newsource.split("\\")[-1]
                                print newname
                                lyr.replaceDataSource(locationFixed, "SDE_WORKSPACE", newname)
                                print "lyr replaced: " + newsource
                        except:
                            if os.path.join(root, n) not in issues:
                                issues.append(os.path.join(root, n))
                            print lyr.name + " is not a feature layer"
                    tables = arcpy.mapping.ListTableViews(map, "", df)
                    for tbl in tables:
                        try:
                            if "TPP_GIS.MCHAMB1." in tbl.dataSource:
                                print "tbl source: " + tbl.dataSource
                                newsource = tbl.dataSource.replace("TPP_GIS.MCHAMB1.", "TPP_GIS.APP_TPP_GIS_ADMIN.")
                                location = newsource.split("\\")[:-2]
                                locationFixed = "\\".join(location)
                                print locationFixed
                                newname = newsource.split("\\")[-1]
                                print newname
                                tbl.replaceDataSource(locationFixed, "SDE_WORKSPACE", newname)
                                print "tbl replaced: " + newsource
                        except:
                            if os.path.join(root, n) not in issues:
                                issues.append(os.path.join(root, n))
                            print tbl.name + " is not a feature layer"
                map.save()
print "success!"
print "the following MXD contained issues with a layer having not dataSource:"
for i in issues:
    print str(i)