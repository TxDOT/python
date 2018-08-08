import arcpy, os
from arcgis.gis import GIS

# Sign in to portal/set workspace
user = "sross_c_TXDOT"
password = "Honeybee2!"
arcpy.SignInToPortal('https://www.arcgis.com', user, password)
arcpy.env.workspace = r"C:\Users\SROSS-C\Documents\ArcGIS\Projects\UpdateServiceTest\MyProject\MyProject.gdb"
portal = "http://www.arcgis.com"
gis = GIS(portal, user, password)

# Set output file names
outdir = r"C:\Users\SROSS-C\Documents\ArcGIS\Projects\UpdateServiceTest\MyProject"

# Reference map to publish
aprx = arcpy.mp.ArcGISProject(r"C:\Users\SROSS-C\Documents\ArcGIS\Projects\UpdateServiceTest\MyProject\MyProject.aprx")
m = aprx.listMaps()[0]

#Grab list of feature classes in map
fcList = sorted(arcpy.ListFeatureClasses())
# #Get list of filenames.sddraft
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

#number of layers to loop through -1
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
    arcpy.AddMessage("Exporting " + str(lyrs) + ".sd ...")
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
        sdItem = gis.content.search("{} AND owner:{}".format(service, user), item_type="Service Definition", sort_field="title", sort_order="asc", max_items=100)[0]
    except IndexError:
        sdItem = "no"
        pass
    arcpy.AddMessage("Working on " + service)
    weblayer = sdItem.title
    if service == weblayer:
        try:
            arcpy.AddMessage("Overwriting " + service)
            sddraft = fcListAll[t]
            sd = sd_output_filename
            arcpy.StageService_server(sddraft, sd)
            sdItem.update(data=sd)
            sdItem.publish(overwrite=True)
            arcpy.AddMessage("Success!")
            t+=1
        except IndexError:
            arcpy.AddMessage("Failure")
            continue
    else:
        try:
            arcpy.AddMessage("Uploading Service Definition" + fcListAll[t] + "...")
            arcpy.StageService_server(fcListAll[t], sd_output_filename)
            arcpy.UploadServiceDefinition_server(sd_output_filename, "My Hosted Services")
            arcpy.AddMessage("Successfully Uploaded service.")
            t+=1
        except:
            arcpy.AddMessage("Failure")
            t+=1
arcpy.AddMessage("Finished")
