__file__ = 'Download_Entire_Service_arcRest_Polyline.py'
__date__ = '4/19/2016'
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
from arcrest.security import AGOLTokenSecurityHandler
from arcrest.agol import FeatureLayer
import os, json, shutil, csv, arcpy, datetime

# this script will download an entire feature service host on AGO. this script is more cumbersome
# than other methods due to restrictions on services published via a web browser instead of an MXD
# this script will only work on polyline type geometry services

# variables
username = "non-enterprise AGO username"
password = "guess what goes here"
feature_service_url = "http://services.arcgis.com/KTcxiTD9dsQw4r7Z/arcgis/rest/services/TxDOT_Projects/FeatureServer/0"
output_folder = "C:\TxDOT\Scripts\python\LRTP\_ProjectsLRTP"
feature_class_name = "TxDOT_Projects_FC"

# the rest should take care of itself
# ---------------------------------------------------------
now = datetime.datetime.now()
month = now.strftime("%m")
day = now.strftime("%d")
year = now.strftime("%Y")
the_date = year + month + day


def downloadData():
    print "beginning data download..."
    proxy_port = None
    proxy_url = None

    agolSH = AGOLTokenSecurityHandler(username=username,
                                      password=password)

    fl = FeatureLayer(
        url=feature_service_url,
        securityHandler=agolSH,
        proxy_port=proxy_port,
        proxy_url=proxy_url,
        initialize=True)

    oid_query_response = fl.query(returnIDsOnly=True)
    oid_list = oid_query_response["objectIds"]
    oid_list.sort()
    list_length = len(oid_list)
    print list_length

    if os.path.exists(output_folder + os.sep + feature_class_name + "_" + the_date + ".gdb"):
        shutil.rmtree(output_folder + os.sep + feature_class_name + "_" + the_date + ".gdb")
    if os.path.isfile(output_folder + os.sep + "Errors.csv"):
        os.remove(output_folder + os.sep + "Errors.csv")
    arcpy.CreateFileGDB_management(output_folder, feature_class_name + "_" + the_date)
    output_fgdb = output_folder + os.sep + feature_class_name + "_" + the_date + ".gdb"

    def updatedQuery(low, high, trigger):
        if low != high:
            updated_query = """"OBJECTID" >= """ + str(low) + " AND " + """"OBJECTID" < """ + str(high)
            if trigger == 1:
                updated_query = """"OBJECTID" >= """ + str(low)
        else:
            updated_query = """"OBJECTID" = """ + str(low)
        return updated_query

    errors = []
    error_fields = []
    fc = ""
    fields = ["SHAPE@"]
    low = 0
    high = 1000
    counter = 0
    while low <= list_length:
        min = oid_list[low]
        try:
            max = oid_list[high]
            trigger = 0
        except:
            totalFixed = list_length - 1
            max = oid_list[totalFixed]
            trigger = 1
        updated_query = updatedQuery(min, max, trigger)
        returned_data = fl.query(where=updated_query,out_fields='*',returnGeometry=True)
        returned_data_string = str(returned_data)
        d = json.loads(returned_data_string)
        print "dictionary compiled."

        if counter == 0:
            wkid = d['spatialReference']['latestWkid']
            sr = arcpy.SpatialReference(wkid)
            arcpy.CreateFeatureclass_management(output_fgdb, feature_class_name, "POLYLINE", "", "DISABLED", "DISABLED", sr)
            fc = output_fgdb + os.sep + feature_class_name
            for field in d['fields']:
                print field["name"]
                error_fields.append(field["name"])
                if field["name"] != "OBJECTID" and field["name"] != "Shape_Length" and field["name"] != "GlobalID":
                    text_length = ""
                    if field["type"] == "esriFieldTypeInteger":
                        type = "LONG"
                    elif field["type"] == "esriFieldTypeSmallInteger":
                        type = "SHORT"
                    elif field["type"] == "esriFieldTypeString":
                        type = "TEXT"
                        text_length = field["length"]
                    elif field["type"] == "esriFieldTypeDouble":
                        type = "DOUBLE"
                    elif field["type"] == "esriFieldTypeFloat":
                        type = "FLOAT"
                    elif field["type"] == "esriFieldTypeDate":
                        type = "DATE"
                    arcpy.AddField_management(fc, field["name"], type, "", "", text_length, field["alias"])
                    fields.append(field["name"])
            errors.append(error_fields)

        cursor = arcpy.da.InsertCursor(fc, fields)
        records = d["features"]
        for record in records:
            try:
                geom = record["geometry"]
                paths = geom["paths"]
                new_geom = arcpy.Array()
                for part in paths:
                    this_part = arcpy.Array()
                    for point in part:
                        this_point = arcpy.Point(point[0], point[1])
                        this_part.append(this_point)
                    new_geom.append(this_part)
                polyline = arcpy.Polyline(new_geom)
            except:
                polyline = arcpy.Polyline(arcpy.Array(arcpy.Array(arcpy.Point(0,0))))
                error_record = []
                for err_fld in error_fields:
                    error_record.append(record["attributes"][err_fld])
                errors.append(error_record)
                print record

            values = [polyline]
            attributes = record["attributes"]
            for field in fields:
                if field != "SHAPE@":
                    values.append(attributes[field])

            cursor.insertRow(values)
            counter += 1
            print str(counter) + "\\" + str(list_length)

        low += 1000
        high += 1000

    no_geom_csv = open(output_folder + os.sep + "Errors.csv", 'wb')
    writer = csv.writer(no_geom_csv)
    writer.writerows(errors)
    no_geom_csv.close()

downloadData()

print "that's all folks!"
