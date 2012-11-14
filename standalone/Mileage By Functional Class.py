import arcpy, os
FC_Frontage_Roads = arcpy.GetParameterAsText(0)
FC_Centerlines = arcpy.GetParameterAsText(1)
Routed_SubFiles = arcpy.GetParameterAsText(2)
District_Boundaries = arcpy.GetParameterAsText(3)
MPO_Boundaries = arcpy.GetParameterAsText(4)
outputFolder = arcpy.GetParameterAsText(5)
scracthSpace = outputFolder + os.sep + "scratchSpace" + os.sep

if not os.path.exists(scracthSpace):
	os.makedirs(scracthSpace)

inputs_to_merge = [Routed_SubFiles, FC_Centerlines, FC_Frontage_Roads]
FC_roadways_merged = scracthSpace + "temp_FC_roadways_merged.shp"
District_Boundaries_w_o_MPO = scracthSpace + "temp_District_Boundaries_w_o_MPO.shp"


intersect_features1 = [FC_roadways_merged, MPO_Boundaries]
FC_roads_by_MP0 = scracthSpace + "temp_FC_roads_by_MPO.shp"

intersect_features2 = [FC_roadways_merged, District_Boundaries_w_o_MPO]
FC_roads_by_District = scracthSpace + "temp_FC_roads_by_District.shp"

Final_FC_Roads_by_MPO = outputFolder + os.sep + "FC_Roads_by_MPO.shp"
Final_FC_Roads_by_Districts = outputFolder + os.sep + "FC_Roads_by_Districts.shp"

arcpy.SetProgressor("step", "Merging... Please Wait (this can take a while)", 0,9,1)
arcpy.AddMessage("Merging Datasets:\n%s\n%s\n%s" % (inputs_to_merge[0],inputs_to_merge[1],inputs_to_merge[2]))
arcpy.Merge_management(inputs_to_merge, FC_roadways_merged)
arcpy.AddMessage("File Created: %s\n" % FC_roadways_merged)
arcpy.SetProgressorPosition()

arcpy.SetProgressorLabel("Erase Analysis...") 
arcpy.AddMessage("Creating Distrct Bounadries without MPOs")
arcpy.Erase_analysis(District_Boundaries, MPO_Boundaries, District_Boundaries_w_o_MPO )
arcpy.AddMessage("File Created: %s\n" % District_Boundaries_w_o_MPO )
arcpy.SetProgressorPosition()

arcpy.SetProgressorLabel("Intersect Analysis...") 
arcpy.AddMessage("Intersecting... %s\nby... %s" % (intersect_features1[0], intersect_features1[1]))
arcpy.Intersect_analysis(intersect_features1, FC_roads_by_MPO, "ALL", "", "LINE")
arcpy.AddMessage("File Created: %s\n" % FC_Roads_by_MPO)
arcpy.SetProgressorPosition()

arcpy.SetProgressorLabel("Intersect Analysis...") 
arcpy.AddMessage("Intersecting... %s\nby... %s" % (intersect_features2[0], intersect_features2[1]))
arcpy.Intersect_analysis(intersect_features2, FC_roads_by_District, "ALL", "", "LINE")
arcpy.AddMessage("File Created: %s\n" % FC_roads_by_District)
arcpy.SetProgressorPosition()

arcpy.SetProgressorLabel("Dissolving by MPO...") 
arcpy.AddMessage("Dissolving... %s\nby... FUNCL_2008 and MPO_LBL" % FC_roads_by_MP0)
arcpy.Dissolve_management(FC_roads_by_MP0, Final_FC_Roads_by_MPO, "FUNCL_2008;MPO_LBL", "", "MULTI_PART", "DISSOLVE_LINES")
arcpy.AddMessage("File Created: %s\n" % Final_FC_Roads_by_MPO)
arcpy.SetProgressorPosition()

arcpy.SetProgressorLabel("Dissolving by District...") 
arcpy.AddMessage("Dissolving... %s\nby... FUNCL_2008 and DIST_NM" % FC_roads_by_District)
arcpy.Dissolve_management(FC_roads_by_District, Final_FC_Roads_by_Districts, "FUNCL_2008;DIST_NM", "", "MULTI_PART", "DISSOLVE_LINES")
arcpy.AddMessage("File Created: %s\n" % Final_FC_Roads_by_Districts)
arcpy.SetProgressorPosition()

arcpy.SetProgressorLabel("Adding Field...")
arcpy.AddMessage("Adding Field TTL_MILES to %s..." % Final_FC_Roads_by_MPO)
arcpy.AddField_management(Final_FC_Roads_by_MPO, "TTL_MILES", "FLOAT", "9", "4", "", "", "NON_NULLABLE", "NON_REQUIRED")
arcpy.AddMessage("Field add complete\n")
arcpy.SetProgressorPosition()

arcpy.SetProgressorLabel("Adding Field...")
arcpy.AddMessage("Adding Field TTL_MILES to %s..." % Final_FC_Roads_by_Districts)
arcpy.AddField_management(Final_FC_Roads_by_Districts, "TTL_MILES", "FLOAT", "9", "4", "", "", "NON_NULLABLE", "NON_REQUIRED")
arcpy.AddMessage("Field add complete\n")
arcpy.SetProgressorPosition()

arcpy.SetProgressorLabel("Calculating Field...")
arcpy.AddMessage("Calculating Total Length in Miles for field TTL_MILES in\n%s" % Final_FC_Roads_by_MPO)
arcpy.CalculateField_management(Final_FC_Roads_by_MPO, "TTL_MILES", "!shape.length@miles!", "PYTHON_9.3")
arcpy.AddMessage("%s - Done!\n" % Final_FC_Roads_by_MPO)
arcpy.SetProgressorPosition()

arcpy.SetProgressorLabel("Calculating Field...")
arcpy.AddMessage("Calculating Total Length in Miles for field TTL_MILES in\n%s" % Final_FC_Roads_by_Districts)
arcpy.CalculateField_management(Final_FC_Roads_by_Districts, "TTL_MILES", "!shape.length@miles!", "PYTHON_9.3")
arcpy.AddMessage("%s - Done!\n" % Final_FC_Roads_by_Districts)
arcpy.ResetProgressor()