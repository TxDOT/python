from Tkinter import *
import tkMessageBox
import os
import arcpy

def generateMaps():
	global MXDValue
	global gridValue
	global defQueryValue
	global outputFolderValue
	global mapTypeValue
		
	def checkPath(val):
		if not os.path.exists(val):
			tkMessageBox.showerror("Error", "\"%s\" is not valid" % val)
			validInput = False
		else:
			validInput = True
		return validInput
		
	validMXDPath = checkPath(MXDValue.get().strip())
	validGridPath = checkPath(gridValue.get().strip())
	validOutputFolder = checkPath(outputFolderValue.get().strip())

	if validMXDPath and validGridPath and validOutputFolder:
		print "Paths are valid, generating PDFs"
		
		mxdLocation = MXDValue.get().strip()
		grid = gridValue.get().strip()
		defQ = defQueryValue.get().strip()
		outputDirectory = outputFolderValue.get().strip()
		mapType = mapTypeValue.get().strip()

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
			arcpy.mapping.ExportToPDF(map, outputFileName, "PAGE_LAYOUT", 640, 480, 300, "BEST", "RGB", True, "ADAPTIVE", "VECTORIZE_BITMAP")

		del map
		del dataFrame
		del cursor
		
	else:
		pass

	return

if __name__ == "__main__":

	interface = Tk()
	interface.title("Create FC PDF Maps")
	interface["height"] = 400
	interface["padx"] = 10
	interface["pady"] = 10

	mxdFrame = Frame(interface)
	mxdFrameLabel = Label(mxdFrame)
	mxdFrameLabel["text"] = "MXD:"
	mxdFrameLabel.pack(side=TOP)
	MXDValue = Entry(mxdFrame)
	MXDValue["width"] = 60
	MXDValue.pack(side=LEFT)
	mxdFrame.pack()

	gridFrame = Frame(interface)
	gridFrameLabel = Label(gridFrame)
	gridFrameLabel["text"] = "Grid:"
	gridFrameLabel.pack(side=TOP)
	gridValue = Entry(gridFrame)
	gridValue["width"] = 60
	gridValue.pack(side=LEFT)
	gridFrame.pack()
	
	defQueryFrame = Frame(interface)
	defQueryFrameLabel = Label(defQueryFrame)
	defQueryFrameLabel["text"] = "DefQ (optional):"
	defQueryFrameLabel.pack(side=TOP)
	defQueryValue = Entry(defQueryFrame)
	defQueryValue["width"] = 60
	defQueryValue.pack(side=LEFT)
	defQueryFrame.pack()
	
	outputFolderFrame = Frame(interface)
	outputFolderLabel = Label(outputFolderFrame)
	outputFolderLabel["text"] = "Output Folder:"
	outputFolderLabel.pack(side=TOP)
	outputFolderValue = Entry(outputFolderFrame)
	outputFolderValue["width"] = 60
	outputFolderValue.pack(side=LEFT)
	outputFolderFrame.pack()

	mapTypeFrame = Frame(interface)
	mapTypeLabel = Label(mapTypeFrame)
	mapTypeLabel["text"] = "Map Type:"
	mapTypeLabel.pack(side=TOP)
	mapTypeValue = Entry(mapTypeFrame)
	mapTypeValue["width"] = 60
	mapTypeValue.pack(side=LEFT)
	mapTypeFrame.pack()

	button = Button(interface, text="Generate PDF Maps", command=generateMaps)
	button.pack()
	interface.mainloop()
