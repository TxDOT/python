import arcpy, os

# Sign in to portal/set workspace
arcpy.SignInToPortal('https://www.arcgis.com', 'Username', 'Password')
arcpy.env.workspace = r"C:\Users\SROSS-C\Documents\ArcGIS\Projects\UpdateServiceTest\MyProject\MyProject.gdb"

# Set output file names
outdir = r"C:\Users\SROSS-C\Documents\ArcGIS\Projects\UpdateServiceTest\MyProject"

# Reference map to publish
aprx = arcpy.mp.ArcGISProject(r"C:\Users\SROSS-C\Documents\ArcGIS\Projects\UpdateServiceTest\MyProject\MyProject.aprx")
m = aprx.listMaps()[0]

#Grab list of feature classes in map
fcList = sorted(arcpy.ListFeatureClasses())
print (fcList)

#Get list of filenames.sddraft
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

#number of layers to loop through -1
lyrlist = 4
# for lyr in m.listLayers():
#   lyrlist.append(lyr)
# print (len(lyrlist))

#Loop through and create sddraft files for each layer
x = 0
while x <= lyrlist:
  for lyrs in m.listLayers():
    sharing_draft = m.getWebLayerSharingDraft("HOSTING_SERVER", "FEATURE", lyrs, lyrs)
    sharing_draft.summary = "My Summary"
    sharing_draft.tags = "GRID_Export"
    sharing_draft.description = "Source: Geospatial Roadway Inventory Database GRID Export"
    sharing_draft.credits = "TxDOT – TPP – Data Management"
    sharing_draft.useLimitations = "Copyright 2018. Texas Department of Transportation. This data was produced for internal use within the Texas Department of Transportation and made available to the public for informational purposes only. Accuracy is limited to the validity of available data as of the date published"
    print (lyrs,sharing_draft)
    # Create Service Definition Draft file
    sharing_draft.exportToSDDraft(fcListAll[x])
    x+=1

#Loop through and upload ead service definition file
finallist = []
t = 0
while t < len(fcList):
  for fc in fcList:
    print ("starting...")
    service = fcList[t]
    #Stage Service
    sd_filename = service + ".sd"
    sd_output_filename = os.path.join(outdir, sd_filename)
    print (service,sd_filename,sd_output_filename)
    arcpy.StageService_server(fcListAll[t], sd_output_filename)
    # Share to portal
    print("Uploading Service Definition...")
    arcpy.UploadServiceDefinition_server(sd_output_filename, "My Hosted Services")
    print("Successfully Uploaded service.")
    t+=1
