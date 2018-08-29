from arcgis.gis import GIS
from arcgis import features
from arcgis.features import FeatureLayerCollection
import glob, os

#Credentials
gis = GIS("https://www.arcgis.com",'Username', "Password")

#ZipGDB file path
#create list of paths
dir = r"C:\Users\SROSS-C\Documents\ArcGIS\Projects\UpdateSericeTest\Shps"
dirlist = []
for file in os.listdir(dir):
  if file.endswith(".zip"):
    dirlist.append(os.path.join(dir,file))

#Add item to AGOL
i = 0
count = 0
while i < len(dirlist):
  # Add item to AGOL
  csv_item1 = gis.content.add({},dirlist[i])
  csv_item1
  #Publish hosted feature layer
  csvlayer1 = csv_item1.publish()
  csvlayer1
  i += 1
  print (i)
  if i >= len(dirlist):
    break

fin = "Finished"
print (fin)
