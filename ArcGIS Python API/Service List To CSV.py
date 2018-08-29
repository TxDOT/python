from arcgis.gis import GIS
import csv
import os

# AGO Credintials
Username = "Username"
Password = "Password"

# Create connection
gis = GIS("https://www.arcgis.com", Username, Password)

# Search and create a list of content
fc = gis.content.search(query="contentstatus: org_authoritative",sort_field="title",sort_order="asc", max_items=100 )

#create folder
AgoList = r'C:\Users\SROSS-C\Desktop\AgoList'
if not os.path.exists(AgoList):
    os.makedirs(AgoList)

#write to csv
with open(r"C:\Users\SROSS-C\Desktop\AgoList\AgoList.csv", "w") as output:
    writer = csv.writer(output, lineterminator='\n')
    for item in fc:
        ItemList = [item.title,item.accessInformation,item.licenseInfo,item.tags]
        writer.writerow(ItemList)
