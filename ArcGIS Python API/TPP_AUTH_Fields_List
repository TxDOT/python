from arcgis.gis import GIS
import csv
import os

# AGO Credintials
Username = "Username"
Password = "Password"
# Create connection
gis = GIS("https://www.arcgis.com", Username, Password)
search_results = gis.content.search("owner: TPP_GIS AND contentstatus: org_authoritative", sort_field="title", sort_order="asc", max_items=1000)

path = r"T:\DATAMGT\MAPPING\Projects\2018\GRID Asset Exports\PublishGRIDExports\AgoList.csv"

try:
  os.remove(path)
except FileNotFoundError:
  pass

i = 0
while i < len(search_results):
    fieldlist = []
    item = search_results[i]
    title = item.title
    layers = item.layers
    itemlayers = layers[0]
    fieldlist.append(title)
    for f in itemlayers.properties.fields:
        fieldlist.append(f['name'])
    with open(r"T:\DATAMGT\MAPPING\Projects\2018\GRID Asset Exports\PublishGRIDExports\AgoList.csv", "a") as output:
        writer = csv.writer(output, lineterminator='\n')
        writer.writerow(fieldlist)
    print(i)
    i+=1
