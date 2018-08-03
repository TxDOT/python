import arcpy
import os, sys
from arcgis.gis import GIS

### Start setting variables
# Set the path to the project
prjPath = r"C:\Users\SROSS-C\Documents\ArcGIS\Projects\UpdateServiceTest\MyProject\MyProject.aprx"
arcpy.env.workspace = r"C:\Users\SROSS-C\Documents\ArcGIS\Projects\UpdateServiceTest\MyProject\MyProject.gdb"
portal = "http://www.arcgis.com" # Can also reference a local portal
user = "sross_c_TXDOT"
password = "Password"
fcList = sorted(arcpy.ListFeatureClasses())


# Update the following variables to match:
# Feature service/SD name in arcgis.com, user/password of the owner account

sd_fs_name = "GRID_Acceleration_Deceleration_Lane"

# Set sharing options
# shrOrg = True
# shrEveryone = False
# shrGroups = ""

### End setting variables

# Local paths to create temporary content
relPath = sys.path[0]
sddraft = os.path.join(relPath, "WebUpdate.sddraft")
sd = os.path.join(relPath, "WebUpdate.sd")
#
# # Create a new SDDraft and stage to SD
print("Creating SD file")
arcpy.env.overwriteOutput = True
prj = arcpy.mp.ArcGISProject(prjPath)
mp = prj.listMaps()[0]

arcpy.mp.CreateWebLayerSDDraft(mp, sddraft, sd_fs_name, "MY_HOSTED_SERVICES", "FEATURE_ACCESS","", True, True)
arcpy.StageService_server(sddraft, sd)

print("Connecting to {}".format(portal))
gis = GIS(portal, user, password)

# Find the SD, update it, publish /w overwrite and set sharing and metadata
print("Search for original SD on portal…")
sdItem = gis.content.search("{} AND owner:{}".format(sd_fs_name, user), item_type="Service Definition")[0]
print("Found SD: {}, ID: {} n Uploading and overwriting…".format(sdItem.title, sdItem.id))
sdItem.update(data=sd)
print("Overwriting existing feature service…")
fs = sdItem.publish(overwrite=True)

# if shrOrg or shrEveryone or shrGroups:
#   print("Setting sharing options…")
#   fs.share(org=shrOrg, everyone=shrEveryone, groups=shrGroups)

print("Finished updating: {} – ID: {}".format(fs.title, fs.id))
