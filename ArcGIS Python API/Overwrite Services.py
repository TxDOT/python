from arcgis.gis import *
from arcgis.features import FeatureLayerCollection
import glob, os

# AGO Credintials
Username = "Username"
Password = "Password"

#Create connection
gis = GIS("https://www.arcgis.com", Username, Password)

#create list of paths
dir = r"C:\Users\SROSS-C\Documents\ArcGIS\Projects\UpdateSericeTest\Shps"
dirlist = []
for file in os.listdir(dir):
  if file.endswith(".zip"):
    dirlist.append(os.path.join(dir,file))

#search for list of feature services on AGOL to be updated
fc = gis.content.search(query= "owner:sross_c_TXDOT", item_type="Feature Layer",sort_field="title",sort_order="asc")

# Loop through item list
i = 0
count = 0
while i < len(dirlist):
  for item in fc:
    title = item.title
    id = item.id
    fs = gis.content.get(id)
    flc = FeatureLayerCollection.fromitem(fs)
    flc.manager.overwrite(dirlist[i])
    count += 1
    print(title, dirlist[i], id, count)
    i+=1

# # overwrite a single feature on AGOL
# fs = gis.content.get('e46f2e92e359477b9580e4a21dc3bcab')
# print (fs)
# flc = FeatureLayerCollection.fromitem(fs)
# print(flc)
# flc.manager.overwrite(r"C:\Users\SROSS-C\Documents\ArcGIS\Projects\UpdateSericeTest\UpdateSericeTest.gdb.zip")
#
# #Check if number of features has changed
# lyr = flc.layers[0]
# check = lyr.query(return_count_only=True)
# print (check)
