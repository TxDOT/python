__file__ = 'Download_Entire_Service_v1'
__date__ = '4/18/2015'
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
import arcpy, datetime, os, urllib, urllib2, json, shutil


# variables
serviceURL = "http://services.arcgis.com/KTcxiTD9dsQw4r7Z/arcgis/rest/services/YES_M/FeatureServer/0"
output_folder = r"C:\TxDOT\Scripts\python\LRTP\_ProjectsLRTP"
feature_class_name = "TxDOT_Projects_FC"
username = "your Non-Enterprise account"
password = "yourpassword"

now = datetime.datetime.now()
month = now.strftime("%m")
day = now.strftime("%d")
year = now.strftime("%Y")
the_date = year + month + day


def generateToken():
    try:
        arcpy.AddMessage('Generating Token')
        tokenURL = 'https://www.arcgis.com/sharing/rest/generateToken'
        params = {'f': 'pjson', 'username': username, 'password': password, 'referer': 'http://www.arcgis.com'}
        req = urllib2.Request(tokenURL, urllib.urlencode(params))
        response = urllib2.urlopen(req)
        data = json.load(response)
        the_token = data['token']
    except:
        the_token = ''
    return the_token


def getObjectIDs(query):
    params = {'where': query, 'returnIdsOnly': 'true', 'token': token, 'f': 'json'}
    req = urllib2.Request(baseURL, urllib.urlencode(params))
    response = urllib2.urlopen(req)
    data = json.load(response)
    print response
    print data
    array = data["objectIds"]
    array.sort()
    print "Object IDs Found"
    return array


def createFC(fs):
    if os.path.exists(output_folder + os.sep + feature_class_name + "_" + the_date + ".gdb"):
            shutil.rmtree(output_folder + os.sep + feature_class_name + "_" + the_date + ".gdb")
    arcpy.CreateFileGDB_management(output_folder, feature_class_name + "_" + the_date)
    fgdb = output_folder + os.sep + feature_class_name + "_" + the_date
    arcpy.CopyFeatures_management(fs, fgdb + ".gdb" + os.sep + feature_class_name)
    newFC = fgdb + ".gdb" + os.sep + feature_class_name
    print "feature class created."
    return newFC


def updatedQuery(low, high, trigger):
    if low != high:
        addition = """"OBJECTID" >= """ + str(low) + " AND " + """"OBJECTID" < """ + str(high)
        if trigger == 1:
            addition = """"OBJECTID" >= """ + str(low)
    else:
        addition = """"OBJECTID" = """ + str(low)
    newQuery = addition
    return newQuery

baseURL = serviceURL + "/query"
fields = '*'
token = generateToken()
where = "1=1"

objectIDs = getObjectIDs(where)
total = len(objectIDs)
print "Total: " + str(total)
totalFixed = total - 1
last = objectIDs[-1]
low = 0
high = 1000
theFC = ""

while low <= total:
    print low
    min = objectIDs[low]
    try:
        max = objectIDs[high]
        trigger = 0
    except:
        max = objectIDs[totalFixed]
        trigger = 1
    OIDquery = updatedQuery(min, max, trigger)
    query = "?where={}&outFields={}&returnGeometry=true&f=json&token={}".format(OIDquery, fields, token)
    fsURL = baseURL + query
    fs = arcpy.FeatureSet()
    fs.load(fsURL)
    print "select completed."
    if low == 0:
        theFC = createFC(fs)
    else:
        arcpy.Append_management(fs, theFC, "NO_TEST")
    low += 1000
    high += 1000

print "that's all folks!!"
