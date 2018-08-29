import arcpy, os
from arcgis.gis import GIS
from arcgis.features import FeatureLayerCollection
import os
import sys

# Sign in to portal/set workspace
user = "Username"
password = "Password"
arcpy.SignInToPortal('https://www.arcgis.com', user, password)
portal = "http://www.arcgis.com"
gis = GIS(portal, user, password)
tag = "Quarterly"
arcpy.AddMessage("Connected to AGO as " + user + "...")

# set workspace gdb.
arcpy.env.workspace = r"C:\Users\SROSS-C\Documents\AGO_Publishing\QuarterlyUpdates\QuarterlyUpdates.gdb"
# Set output file names
outdir = r"C:\Users\SROSS-C\Documents\AGO_Publishing\QuarterlyUpdates"
# Reference map to publish
aprx = arcpy.mp.ArcGISProject(r"C:\Users\SROSS-C\Documents\AGO_Publishing\QuarterlyUpdates\QuarterlyUpdates.aprx")
m = aprx.listMaps()[0]

#Grab list of feature classes in map
fcList = arcpy.ListFeatureClasses()

#Get list of filenames.sddraft
arcpy.AddMessage("Getting list of filenames .sddraft...")
fcListAll =[]
i = 0
while i < len(fcList):
  for fc in fcList:
    service = fcList[i]
    sddraft_filename = service + ".sddraft"
    sddraft_output_filename = os.path.join(outdir, sddraft_filename)
    fcListAll.append(sddraft_output_filename)
    i+=1
fcListAll.sort()
print (fcListAll)

#Get the number of layers to loop through
lyrlist = []
for lyr in m.listLayers():
  lyrlist.append(lyr)
lyrlist1 = len(lyrlist) - 1

#Loop through and create sddraft files for each layer
arcpy.AddMessage("Creating sddraft files...")
x = 0
while x <= lyrlist1:
  for lyrs in m.listLayers():
    sharing_draft = m.getWebLayerSharingDraft("HOSTING_SERVER", "FEATURE", lyrs, lyrs)
    sharing_draft.credits = "TxDOT – TPP – Data Management"
    sharing_draft.useLimitations = "Copyright 2018. Texas Department of Transportation. This data was produced for internal use within the Texas Department of Transportation and made available to the public for informational purposes only. Accuracy is limited to the validity of available data as of the date published"
    arcpy.AddMessage("Exporting " + str(lyrs) + ".sddraft...")
    sharing_draft.exportToSDDraft(fcListAll[x])     # Create Service Definition Draft file
    x+=1

#Loop through and upload ead service definition file
finallist = []
t = 0
while t < len(fcList):
  for fc in fcList:
    arcpy.AddMessage("Starting...")
    service = fcList[t]
    sd_filename = service + ".sd"
    sd_output_filename = os.path.join(outdir, sd_filename)
    try:
        os.remove(sd_output_filename)
    except FileNotFoundError:
        pass
    try:
        sdItem = gis.content.search("{} AND owner:{} AND tags:{}".format(service, user, tag), item_type="Service Definition", sort_field="title", sort_order="asc", max_items=100)[0]
    except IndexError:
        sdItem = "no"
        pass
    arcpy.AddMessage("Working on " + service + "...")
    weblayer = sdItem.title
    if service == weblayer:
        try:
            arcpy.AddMessage("Overwriting " + service + "...")
            sddraft = fcListAll[t]
            sd = sd_output_filename
            arcpy.StageService_server(sddraft, sd)
            sdItem.update(data=sd)
            sdItem.publish(overwrite=True)
            arcpy.AddMessage("Successfully published " + service)
            t+=1
        except IndexError:
            arcpy.AddMessage("Failure to publish " + service)
            continue
    else:
        try:
            arcpy.AddMessage("Uploading Service Definition " + fcListAll[t] + "...")
            arcpy.StageService_server(fcListAll[t], sd_output_filename)
            arcpy.UploadServiceDefinition_server(sd_output_filename, "My Hosted Services")
            arcpy.AddMessage("Successfully Uploaded " + service)
            t+=1
        except:
            arcpy.AddMessage("Failure to publish " + fcListAll[t])
            t+=1
arcpy.AddMessage("Successfully published services to AGO.")

# Remove underscores from titles
arcpy.AddMessage("Removing underscores from titles...")
# Search and create a list of content
fc = gis.content.search(query="owner: TPP_GIS AND type: Feature Service AND tags: Quarterly",sort_field="title",sort_order="asc", max_items=100 )
# Loop through item list
for item in fc:
  title = item.title
  newtitle = title.replace("_"," ")
  arcpy.AddMessage("Changing " + title + " to " + newtitle + "...")
  item.update(item_properties={'title':newtitle})
  print (newtitle)

arcpy.AddMessage("Enabling Export...")
search_result= gis.content.search("owner: TPP_GIS AND type: Feature Service AND tags: Quarterly", sort_field="title", sort_order="asc", max_items=1000)
b = 0
while b < (len(search_result)):
    item = search_result[b]
    flc = FeatureLayerCollection.fromitem(item)
    update_dict = {"capabilities": "Query,Extract"}
    flc.manager.update_definition(update_dict)
    arcpy.AddMessage(item)
    b+=1

number = len(fc)
arcpy.AddMessage("Finished publishing " + str(number) + " layers!")
