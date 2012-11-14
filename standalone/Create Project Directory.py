import os
import shutil
import time
import arcpy
from easygui import *

def proj_Menu():
    #Collect user name information
    userName = (os.path.expanduser("~/"))[9:16]
    # Ask user for project type selection
    msg1 = "What type of project are you creating?"
    title1 = "Project Type"
    choices1 = ["1. Data Transmittal", "2. Minute Order", "3. Special Map", "4. Training Map", "5. Other"]
    ansMenu = choicebox(msg1, title1, choices1)
    
    #Assign filepath by project type
    if ansMenu == '1. Data Transmittal':
        tmYR = str(time.localtime()[0])
        path = (r"T:\DATAMGT\MAPPING\Data Transmittals" + "\\" + tmYR)
        
    elif ansMenu == '2. Minute Order':
        tmYR = str(time.localtime()[0])
        path = (r"T:\DATAMGT\MAPPING\Special Maps" + "\\" + tmYR + "\Minute Orders")
        msg2 = "What's the intent of the Minute Order?"
        title2 = "Minute Order"
        choices2 = ["1. New Designation", "2. Re-Designation", "3. Proposed Highway", "4. Removal"]
        moType = choicebox(msg2, title2, choices2)
        
        #Assign Minute Order type
        if moType == '1. New Designation':
            moChange = "New Designation"
        if moType == '2. Re-Designation':
            moChange = "Re-Designation"
        if moType == '3. Proposed Highway':
            moChange = "Proposed Highway"
        if moType == '4. Removal':
            moChange = "Removal"
            
    elif ansMenu == '3. Special Map':
        tmYR = str(time.localtime()[0])
        path = (r"T:\DATAMGT\MAPPING\Special Maps" + "\\" +tmYR)
        
    elif ansMenu == '4. Training Map':
        path = r"T:\DATAMGT\MAPPING\Training"
        
    else:
        msg7 = "What is the filepath of your working directory?"
        path = diropenbox(msg7)
        
#Name the project
    msg3 = "What is the project Name?"
    Title3 = "Poject Name"
    projName = enterbox(msg3, Title3)
    
#Ask for a project plan
    msg4 = "Would you like to include a project plan?"
    Title4 = "Project Plan"
    choices4 = ["Yes", "No"]
    ansPlan = buttonbox(msg4, choices=choices4)
    
#Ask user for a project description
    msg10 = "Please enter a short description of the project."
    title10 = "Metadata"
    txtSummary = textbox(msg10, title10)
    
#Create folder directory
    folderPDF = (path + "\\" + projName + "\PDF")
    folderGeoData = (path + "\\" + projName + "\Geographic Data")
    folderScripts = (path + "\\" + projName + "\Scripts")
    folderMaps = (path + "\\" + projName + "\Maps")
    folderDoc = (path + "\\" + projName+ "\Documentation")
    
#Change the location of the Project Template here:
    projTemp = r"T:\DATAMGT\MAPPING\Personal Folders\David H\Scripts\ProjectTemplate.doc"
    newProjPlan = (folderDoc + "\\" + projName + ".doc")
    folderList = [folderPDF, folderGeoData, folderScripts, folderMaps, folderDoc]
    for x in folderList:
        if not os.path.exists(x):
            os.makedirs(x)
    if ansPlan is 'Yes':
        shutil.copyfile(projTemp,newProjPlan)
    else:
        pass
    print " "
    projDirectory = (path + "\\" + projName)
    print projDirectory
    
#Open the file directory in Windows Explorer
    msg5 = "Would you like to begin?"
    choices5 = ["Yes", "No"]
    startFile = buttonbox(msg5, choices = choices5)
    mxdTemplate = r'T:\DATAMGT\MAPPING\Personal Folders\David H\Scripts\_Templates\Letter 8.5x11\_Minute Order Base Map Portrait_8.5x11_DavidH.mxd'
    newMXD = (folderMaps + "\\" + projName + ".mxd")
    
    #Confirm begin editing
    if startFile == "Yes":
        msg8 = "Would you like to create a project map document?"
        choices8 = ["Yes", "No"]
        createMXD = buttonbox(msg8, choices = choices8)
        
        #Confirm create new mxd
        if createMXD == "Yes":
            
            #Define standard layers
            lyrRoadways = arcpy.mapping.Layer(r"T:\DATAMGT\MAPPING\Personal Folders\David H\Scripts\_Templates\Layers\TXDOT_Roadways.lyr")
            lyrDistricts = arcpy.mapping.Layer(r"T:\DATAMGT\MAPPING\Personal Folders\David H\Scripts\_Templates\Layers\Districts.lyr")
            lyrCounties = arcpy.mapping.Layer(r"T:\DATAMGT\MAPPING\Personal Folders\David H\Scripts\_Templates\Layers\Counties.lyr")
            lyrCity = arcpy.mapping.Layer(r"T:\DATAMGT\MAPPING\Personal Folders\David H\Scripts\_Templates\Layers\City.lyr")
            
            #Create mxd copy from template
            shutil.copyfile(mxdTemplate,newMXD)
            
            #Assign valriable to new mxd
            mxd = arcpy.mapping.MapDocument(newMXD)
            df = arcpy.mapping.ListDataFrames(mxd)[0]
            
            #Ask user for layers
            msg9 = 'Add Layers'
            choices9 = ["1. TxDOT Roadways", "2. Districts", "3. Counties", "4. Cities"]
            addLayers = multchoicebox(msg9, choices = choices9)
            
            #Open new mxd and add selected layers
            if choices9[0] in addLayers:
                arcpy.mapping.AddLayer(df, lyrRoadways)
            if choices9[1] in addLayers:
                arcpy.mapping.AddLayer(df, lyrDistricts)
            if choices9[2] in addLayers:
                arcpy.mapping.AddLayer(df, lyrCounties)
            if choices9[3] in addLayers:
                arcpy.mapping.AddLayer(df, lyrCity)
                
            #Refresh mxd and save with added layers
            mapID = int(time.time())
            txtMapID = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "txtMapID")[0]
            txtMapID.text = mapID
            
            #Add metadata information to the Map Document Properties
            mxd.author = userName
            mxd.summary = txtSummary
            mxd.credits = 'TPP-GIS'
            mxd.tags = str(mapID)
            
            arcpy.RefreshActiveView()
            mxd.save()
            
            #Open mxd and project file folder
            os.startfile(newMXD)
            os.startfile(projDirectory)
        else:
            pass
    else:
        pass
    
# Modify or create (if not existing) a general log file for all logged projects
# Change the location of the general log file here:
    logFile = r"T:\\DATAMGT\\MAPPING\\Personal Folders\\David H\\Scripts\\ProjectLogFile.txt"
    
#Record directory creation in general log
    with open(logFile, "a") as log:
        log.write("\n" + str(mapID) + ", " + time.ctime() + ", " + userName + ", " + projName + ", " + projDirectory + ", " + txtSummary)
        
#Create a log file specifically for minute orders
#Change the location of the Minute Order log file here:
    moLogFile = r"T:\\DATAMGT\\MAPPING\\Personal Folders\\David H\\Scripts\\MinuteOrderProjectLogFile.txt"
    
#Log minute order specifics into Minute Order log file
    with open(moLogFile, "a") as log:
        log.write("\n" + str(mapID) + ", " + time.ctime() + ", " + moChange + ", " + userName + ", " + projName + ", " + projDirectory+ ", " + txtSummary)
proj_Menu()
