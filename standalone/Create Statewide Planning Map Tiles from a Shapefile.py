import arcpy, os

mxdLocation = arcpy.GetParameterAsText(0)
grid = arcpy.GetParameterAsText(1)
defQ = arcpy.GetParameterAsText(2)
outputDirectory = arcpy.GetParameterAsText(3)
fileType = arcpy.GetParameterAsText(4)

mxd = arcpy.mapping.MapDocument(mxdLocation)
dataFrame = arcpy.mapping.ListDataFrames(mxd)[0]

if defQ == "":
	cursor = arcpy.SearchCursor(grid)
else:
	cursor = arcpy.SearchCursor(grid, defQ)

for row in cursor:
	extent = row.shape.extent
	dataFrame.extent = extent
	arcpy.RefreshActiveView()
	
	if grid[-4:] == ".shp":
		zLevelDir = str(os.sep + grid.split("\\")[-1].split(".")[0]) 
	else:
		zLevelDir = str(os.sep + grid.split("\\")[-1])

	outputFileName = str(row.TILE_NM)
	outputFileLocation = outputDirectory + zLevelDir
	
	if not os.path.exists(outputFileLocation):
		os.makedirs(outputFileLocation)
	
	arcpy.AddMessage( "Exporting Tile: %s" % row.TILE_NM )
	if fileType == "PNG":
		arcpy.mapping.ExportToPNG(mxd, outputFileLocation + os.sep + outputFileName + ".png")
	elif fileType == "PDF":
		arcpy.mapping.ExportToPDF(mxd, outputFileLocation + os.sep + outputFileName + ".pdf")
	elif fileType == "GIF":
		arcpy.mapping.ExportToGIF(mxd, outputFileLocation + os.sep + outputFileName + ".gif", 1056,1056,96,"FALSE","8-BIT_PALETTE","NONE","255,255,255","211,255,190","FALSE")

del mxd
del dataFrame
del cursor