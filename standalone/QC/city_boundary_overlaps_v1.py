__file__ = 'city_boundary_overlaps_v1'
__date__ = '5/16/2016'
__author__ = 'ABREZNIC'
"""
The MIT License (MIT)

Copyright (c) 2016 Texas Department of Transportation
Author: Adam Breznicky

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
import arcpy, os, datetime, csv
from arcpy import env

# user set variables
output_folder = "C:\\TxDOT\\Scripts\\python\\QC\\city_county_overlaps"
comanche_name = "Connection to Comanche.sde"
fc_street_query = "RTE_PRFX = 6"
local_street_query = "RTE_PRFX = 7"
county_road_query = "RTE_PRFX = 1"

# reference variables
print "connecting..."
comanche = "Database Connections" + os.sep + comanche_name
comanche_cities = comanche + os.sep + "TPP_GIS.APP_TPP_GIS_ADMIN.City_Editing\\TPP_GIS.APP_TPP_GIS_ADMIN.Cities_Editing"
comanche_roads = comanche + os.sep + "TPP_GIS.APP_TPP_GIS_ADMIN.GRID_Export\\TPP_GIS.APP_TPP_GIS_ADMIN.Roadways_GRID_Export"
now = datetime.datetime.now()
the_date = now.strftime("%Y") + now.strftime("%m") + now.strftime("%d")


# ------------------------------------
# create working dbase and copy data into it
print "creating working database"
arcpy.CreateFileGDB_management(output_folder, "Overlap_Working_" + the_date + ".gdb")
dbase = output_folder + os.sep + "Overlap_Working_" + the_date + ".gdb"
env.workspace = dbase

print "copying into the working database:"
print "cities"
arcpy.Copy_management(comanche_cities, "Cities")
print "fc streets"
arcpy.Select_analysis(comanche_roads, "FC_Streets", fc_street_query)
print "local streets"
arcpy.Select_analysis(comanche_roads, "Local_Streets", local_street_query)
print "county roads"
arcpy.Select_analysis(comanche_roads, "County_Roads", county_road_query)


# ---------------------------------
# break geometry at city boundaries and remove all the segments which are correct
print "breaking geometry and removing correct segments:"

print "fc streets"
arcpy.Identity_analysis("FC_Streets", "Cities", "Overlaps_FC", "NO_FID")
dictionary = {}
cursor = arcpy.da.SearchCursor("Overlaps_FC", ["GID", "CITY_NM"])
for row in cursor:
    if row[1] != "":
        key = str(row[0])
        dictionary[key] = row[1]
del cursor
del row
print "dictionary built"
cursor = arcpy.da.UpdateCursor("Overlaps_FC", ["GID", "CITY_NM"])
for row in cursor:
    if row[1] == "":
        try:
            key = str(row[0])
            row[1] = dictionary[key]
            cursor.updateRow(row)
        except:
            print row[0], row[1]
    else:
        cursor.deleteRow()
del cursor
del row

print "local streets"
arcpy.Identity_analysis("Local_Streets", "Cities", "Overlaps_LS", "NO_FID")
dictionary = {}
cursor = arcpy.da.SearchCursor("Overlaps_LS", ["GID", "CITY_NM"])
for row in cursor:
    if row[1] != "":
        key = str(row[0])
        dictionary[key] = row[1]
del cursor
del row
print "dictionary built"
cursor = arcpy.da.UpdateCursor("Overlaps_LS", ["GID", "CITY_NM"])
for row in cursor:
    if row[1] == "":
        try:
            key = str(row[0])
            row[1] = dictionary[key]
            cursor.updateRow(row)
        except:
            print row[0], row[1]
    else:
        cursor.deleteRow()
del cursor
del row

print "county roads"
arcpy.Intersect_analysis(["County_Roads", "Cities"], "Overlaps_CR", "NO_FID")


# -------------------------------------------
print "updating DFO and measure fields"
data = [["GID", "RTE_RB_NM", "CITY_NM", "BEGIN_DFO", "END_DFO", "SEG_LEN", "Feature_Class"]]
feature_classes = ["Overlaps_FC", "Overlaps_LS", "Overlaps_CR"]
for fc in feature_classes:
    print fc
    cursor = arcpy.da.UpdateCursor(fc, ["RTE_RB_NM", "BEGIN_DFO", "END_DFO", "SEG_LEN", "SHAPE@LENGTH", "SHAPE@", "GID", "CITY_NM"])
    for row in cursor:
        meters = row[4]
        miles = meters * 0.000621371192
        # length = float(format(float(miles), '.3f'))
        m_min = row[5].extent.MMin
        m_max = row[5].extent.MMax
        row[1] = m_min
        row[2] = m_max
        row[3] = miles
        cursor.updateRow(row)
        record = [row[6], row[0], row[7], m_min, m_max, miles, fc]
        data.append(record)
    del cursor
    del row

print "writing CSV"
final = open(output_folder + os.sep + "Overlap_Report_" + the_date + ".csv", 'wb')
writer = csv.writer(final)
writer.writerows(data)
final.close()

print "that's all folks!!"
