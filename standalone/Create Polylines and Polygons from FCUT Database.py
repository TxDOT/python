import arcpy, os, sys
from arcpy import env

## FILE NAMES, LOCATIONS, AND OPTIONS
outputFolder = arcpy.GetParameterAsText(0)			# Path to output folder
if len(outputFolder) == 0:
	outputFolder = sys.path[0] + os.sep + "workspace"
lineworkFile = outputFolder + "\\linework.shp"		# Name of LINEWORK output file
polygonFile = outputFolder + "\\polygons.shp"		# Name of POLYGON output file
env.overwriteOutput = True 							# Overwrite existing output files (if any)

## FCUT DATABASE INFORMATION
dataSource = arcpy.GetParameterAsText(1)# Path to FCUT Database
table = arcpy.SearchCursor(dataSource) 	# FCUT Database Cursor

## TEMPORARY FEATURE & DATA STORAGE
lineworkFeatures = []					# Linework FEATURE storage
lineworkData = []						# Linework DATA storage
polygonFeatures = []					# Polygon FEATURE storage
polygonData = []						# Polygon DATA Storage

## FUNCTION DECLARATIONS
def createFolder(path):
	""" Creates a new folder at the specified path, or a new folder for each path in a list, ONLY IF the folder does not exist """

	if isinstance(path, basestring):
		if not os.path.exists(path):
			os.makedirs(path)
	elif isinstance(path, list):
		for p in path:
			createFolder(p)
	
	return path

def createPolyline(coordText):
	""" Creates a new record in LINEWORKFEATURES for all coords found in COORDTEXT """
	
	point = arcpy.Point()
	array = arcpy.Array()
	
	for coordPair in coordText:
		try:
			point.X = coordPair.split(",")[0]
			point.Y = coordPair.split(",")[1]
			array.add(point)
		except (RuntimeError, TypeError, NameError) as e:
			errorMessage = "LINE ERROR:\n%s\n%s" % (coordPair, e)
			arcpy.AddMessage(errorMessage)
			print errorMessage
			pass

	polyline = arcpy.Polyline(array)
	lineworkFeatures.append(polyline)
	array.removeAll()
	
	return

def createPolygon(coordText):
	""" Creates a new record in POLYGONFEATURES for all coords found in COORDTEXT """
	
	point = arcpy.Point()
	array = arcpy.Array()

	for coordPair in coordText:
		try:
			point.X = coordPair.split(",")[0]
			point.Y = coordPair.split(",")[1]
			array.add(point)
		except (RuntimeError, TypeError, NameError) as e:
			errorMessage = "POLYGON ERROR:\n%s\n%s" % (coordPair, e)
			arcpy.AddMessage(errorMessage)
			print errorMessage
			pass

	polygon = arcpy.Polygon(array)
	polygonFeatures.append(polygon)
	array.removeAll()
	
	return

def createFields(shapeFile):
	""" Adds the fields in FIELDLIST to the SHAPEFILE """
	
	fieldList = ["FUNCL_ID", "USER_ID", "RTE_NM", "FROM_DSCR", "TO_DSCR", "FCUT_CMNT", "RTE_LNG_MS", "FROM_DT", "TO_DT", "ORGNZ_NM", "REVW_FLAG", "REGN_CMNT", "TPP_FLAG", "REVW_DT", "TPP_WRK_DT"]

	for fieldName in fieldList:
		arcpy.AddField_management(shapeFile, fieldName, "TEXT")

	return

def populateFields(shapeFile, data):
	""" Adds DATA to the SHAPEFILE (Matching fields must already be added by CREATEFIELDS)"""
	
	fieldList = ["FUNCL_ID", "USER_ID", "RTE_NM", "FROM_DSCR", "TO_DSCR", "FCUT_CMNT", "RTE_LNG_MS", "FROM_DT", "TO_DT", "ORGNZ_NM", "REVW_FLAG", "REGN_CMNT", "TPP_FLAG", "REVW_DT", "TPP_WRK_DT"]
	rows = arcpy.UpdateCursor(shapeFile)
	d = 0
	
	for row in rows:
		i = 0
		for value in data[d]:
			row.setValue(fieldList[i], str(value))
			rows.updateRow(row)
			
			if i == len(fieldList) - 1:
				i = 0
			else:
				i += 1
		
		if d == len(data) - 1:
			d = 0
		else:
			d += 1
	
	return

def defineProjection(shapeFile):
	""" Defines the projection of SHAPEFILE to NAD 83 """
	
	projection = str(arcpy.GetInstallInfo().values()[2]) + "Coordinate Systems\\Geographic Coordinate Systems\\North America\\NAD 1983.prj"
	if os.path.exists(projection):
		arcpy.DefineProjection_management(shapeFile, projection)
	else:
		noProjection = "Could not find projection file, shapefile projection will be undefined\n%s" % projection
		arcpy.AddMessage(noProjection)
		print noProjection

	return

## BEGIN EXEC
for row in table:
	coordText = str(row.GEOG_COORD_TXT).split(',0')[0:-1]	# Location Information
	rowValues = [row.FUNCL_CLASS_ID, row.EDIT_USER_ID, row.RTE_NM, row.FROM_LMT_DSCR, row.TO_LMT_DSCR, row.FCUT_CMNT, row.RTE_LNGTH_MS, row.FROM_DT, row.TO_DT, row.ADMN_ORGNZ_NM, row.REGN_REVW_FLAG, row.REGN_CMNT, row.TPP_WRK_FLAG, row.REGN_REVW_DT, row.TPP_WRK_DT]

	if int(row.FUNCL_CLASS_ID) == 0: # Check if feature is a polygon or a line
		isPoly = True
	else:
		isPoly = False
	
	if not isPoly:
		createPolyline(coordText)		# Send to line handler
		lineworkData.append(rowValues)	# Store linework row values
	elif isPoly:
		createPolygon(coordText)		# Send to polygon handler
		polygonData.append(rowValues) 	# Store polygon row values

try:
	createFolder(outputFolder)
	
	arcpy.CopyFeatures_management(lineworkFeatures, lineworkFile)
	arcpy.CopyFeatures_management(polygonFeatures, polygonFile)
	done1 = "\n* * * Created Features\n%s\n%s\n" % (lineworkFile, polygonFile)
	arcpy.AddMessage(done1)
	print done1
	
	createFields(lineworkFile)
	createFields(polygonFile)
	done2 = "* * * Added fields to Features"
	arcpy.AddMessage(done2)
	print done2
	
	populateFields(lineworkFile, lineworkData)
	populateFields(polygonFile, polygonData)
	done3 = "* * * Populated Feature fields"
	arcpy.AddMessage(done3)
	print done3
	
	defineProjection(polygonFile)
	defineProjection(lineworkFile)
	done4 = "* * * Defined Feature Projections"
	arcpy.AddMessage(done4)
	print done4
	
except Exception as err:
	arcpy.AddMessage(err)
	print err

# Clear Locks (if any)
del lineworkFeatures
del lineworkData
del polygonFeatures
del polygonData
del table