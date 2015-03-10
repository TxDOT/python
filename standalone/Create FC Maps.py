import arcpy, os

mxdLocation = arcpy.GetParameterAsText(0)
grid = arcpy.GetParameterAsText(1)
defQ = arcpy.GetParameterAsText(2)
outputDirectory = arcpy.GetParameterAsText(3)
mapType = arcpy.GetParameterAsText(4)

map = arcpy.mapping.MapDocument(mxdLocation)
dataFrame = arcpy.mapping.ListDataFrames(map)[0]
cursor = arcpy.SearchCursor(grid, defQ)

for row in cursor:
	cityName = str(row.CITY_NM)
	districtName = str(row.DIST_NM)
	indexType = str(row.DIST_NM)
	sheetNumber = str(int(row.MAP_ID))
	
	txtSheet = arcpy.mapping.ListLayoutElements(map, "TEXT_ELEMENT", "Sheet")[0]
	txtDistrict = arcpy.mapping.ListLayoutElements(map, "TEXT_ELEMENT", "Title")[0]
	scaleBar = arcpy.mapping.ListLayoutElements(map, "", "Alternating Scale Bar")[0]

	txtDistrict.text = "2010 Functional Classify Update - %s District" % districtName
	
	if mapType == "city":
		scaleBar.elementWidth = 5.2
		outputDirCity = (outputDirectory + os.sep + districtName + os.sep + "City")
		if not os.path.exists(outputDirCity):
			os.makedirs(outputDirCity)
		txtSheet.text = "%s - %s" % (cityName, sheetNumber)
		outputFileName = outputDirCity + os.sep + districtName + " District-" + "City of " + cityName + "-" + sheetNumber + ".pdf"
	if mapType == "district":
		scaleBar.elementWidth = 5
		outputDirDistrict = (outputDirectory + os.sep + districtName + os.sep +  "District")
		if not os.path.exists(outputDirDistrict):
			os.makedirs(outputDirDistrict)
		txtSheet.text = "Sheet - %s" % sheetNumber
		outputFileName = outputDirDistrict + os.sep + districtName + " District-" + sheetNumber + ".pdf"
	if mapType == "index":
		outputDirIndex = (outputDirectory + os.sep + districtName + os.sep + "Index")
		if not os.path.exists(outputDirIndex):
			os.makedirs(outputDirIndex)
		txtSheet.text = "%s Index" % indexType
		outputFileName = outputDirIndex + os.sep + districtName + " District-" + indexType + " Index" + ".pdf"
	extent = row.shape.extent
	dataFrame.extent = extent
	
	arcpy.RefreshActiveView()
	arcpy.AddMessage( "Printing %s PDF...\n%s" % (mapType, outputFileName))
	arcpy.mapping.ExportToPDF(map, outputFileName)

del map
del dataFrame
del cursor