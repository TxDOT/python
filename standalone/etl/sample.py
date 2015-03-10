import arcpy

mxd = arcpy.mapping.MapDocument("CURRENT")
dataFrame = arcpy.mapping.ListDataFrames(mxd)[0]
layers = arcpy.mapping.ListLayers(mxd,"",dataFrame)

def init(layer):
	cursor = arcpy.SearchCursor(layer)
	shapefield = arcpy.Describe(layer).ShapeFieldName
	
	for row in cursor:
		action 	= row.getValue('action')
		routeID = row.getValue('RTE_ID')
		routeGeometry = row.getValue(shapefield).getPart()
		
		for coords in routeGeometry:
			X = [coords[0].X, coords[len(coords)-1].X]
			Y = [coords[0].Y, coords[len(coords)-1].Y]
			M = [coords[0].M, coords[len(coords)-1].M]
			
			arcpy.AddMessage("RouteID: %s" 					% routeID)
			arcpy.AddMessage("ACTION: %s" 					% action)
			arcpy.AddMessage("M Start: %s \nM End: %s" 		% (M[0], M[1]))
			arcpy.AddMessage("X Start: %s \nX End: %s" 		% (X[0], X[1]))
			arcpy.AddMessage("Y Start: %s \nY End: %s\n" 	% (Y[0], Y[1]))
			arcpy.AddMessage("Total M: %s \n" 				% math.fabs(M[0]-M[1]))

for layer in layers:
	roadwayDatasetName = 'sample' # 'TPP_GIS.MCHAMB1.TXDOT_Roadways'
	if layer.datasetName == roadwayDatasetName:
		init(layer)