def archive():
    """
    Create an archive of your MyModules script and push the working script to the main folder.
    """
    import os
    import time
    import shutil
    directory = r"C:\DATAMGT\Scripts\MyModules"
    workingCopy = r"C:\DATAMGT\Scripts\MyModules\MyModules_WorkingCopy.py"
    archiveTime = str(time.localtime()[2]) + str(time.localtime()[1]) + str(time.localtime()[0]) + "_" + str(time.localtime()[3]) + str(time.localtime()[4])
    archive = (directory + os.sep + "Archive" + archiveTime + ".py")
    MyModulesMain = r"C:\Python26\ArcGIS10.0\Lib\site-packages\MyModules.py"
    shutil.copyfile(MyModulesMain,archive)
    shutil.copyfile(workingCopy,MyModulesMain)
    del directory
    del workingCopy
    del archiveTime
    del archive
    
def Checklist(directory,extension='All'):
    """
    Create a checklist file in "txt" format for any folder - list all files by name.
    """
    import os
    checkFile = directory + os.sep + 'Checklist.txt'
    file1 = open(checkFile,"w")
    dirList = os.listdir(directory)
    for fname in dirList:
        if extension == 'All':
            file1.write(str(fname) + "\n")
        else:
            if fname.endswith(extension):
                file1.write(str(fname) + "\n")
    file1.close()
    print 'Done!'

def Project_Menu():
    """
    Through a defined menu, allows a user to select a project category, create a new folder, and optionally add a project plan document.
    """
    import os,shutil,time
# Determine project type and location
    ansMenu = raw_input("What type of project are you creating?\n\n 1 - Data Transmittal\n 2 - Minute Order\n 3 - Special Map\n 4 - Training Map\n 5 - Other Location\n\nEnter Selection: ")
    if ansMenu == '1':
        tmYR = str(time.localtime()[0])
        path = (r"T:\DATAMGT\MAPPING\Data Transmittals" + "\\" + tmYR)
    elif ansMenu == '2':
        tmYR = str(time.localtime()[0])
        path = (r"T:\DATAMGT\MAPPING\Special Maps" + "\\" + tmYR + "\Minute Orders")
        moType = raw_input("\nWhat's the intent of the Minute Order?\n\n 1 - New Designation\n 2 - Re-Designation\n 3 - Proposed Highway\n 4 - Removal\n\nEnter Selection: ")
        if moType == '1':
            moChange = "New Designation"
        if moType == '2':
            moChange = "Re-Designation"
        if moType == '3':
            moChange = "Proposed Highway"
        if moType == '4':
            moChange = "Removal"
    elif ansMenu == '3':
        tmYR = str(time.localtime()[0])
        path = (r"T:\DATAMGT\MAPPING\Special Maps" + "\\" + tmYR)
    elif ansMenu == '4':
        path = r"T:\DATAMGT\MAPPING\Training"
    else:
        path = raw_input("\nWhat is the filepath of your working directory?\n\nPath: ")   
# Name the project
    projName = raw_input("\nWhat is the project name?: ")
# Ask for a project plan
    ansPlan = raw_input("\nWould you like to include a project plan? \n\nY or N: ")
# Create folder directory
    folderPDF = (path + "\\" + projName + "\PDF")
    folderGeoData = (path + "\\" + projName + "\Geographic Data")
    folderScripts = (path + "\\" + projName + "\Scripts")
    folderMaps = (path + "\\" + projName + "\Maps")
    folderDoc = (path + "\\" + projName + "\Documentation")
# Change the location of the Project Template here:
    projTemp = r"T:\DATAMGT\MAPPING\Personal Folders\David H\Scripts\ProjectTemplate.doc"
    newProjPlan = (folderDoc + "\\" + projName + ".doc")
    folderList = [folderPDF,folderGeoData,folderScripts,folderMaps,folderDoc]
    for x in folderList:
        if not os.path.exists(x):
            os.makedirs(x)
    if ansPlan is 'Y':
        shutil.copyfile(projTemp,newProjPlan)
    else:
        pass
    print " "
    projDirectory = (path + "\\" + projName)
    print projDirectory
# Open the file directory in Windows Explorer
    os.startfile(projDirectory)
# Modify or create (if not existing) a general log file for all logged projects
# Change the location of the general log file here:
    logFile = r"T:\\DATAMGT\\MAPPING\\Personal Folders\\David H\\Scripts\\ProjectLogFile.txt"
# Collect user name information
    userName = (os.path.expanduser("~/"))[9:16]
# Record directory creation in general log
    with open(logFile,"a") as log:
        log.write("\n" + time.ctime() + ", " + userName + ", " + projName + ", " + projDirectory)
# Create a log file specifically for minute orders
# Change the location of the Minute Order log file here:
    moLogFile = r"T:\\DATAMGT\\MAPPING\\Personal Folders\\David H\\Scripts\\MinuteOrderProjectLogFile.txt"
# Log minute order specifics into Minute Order log file
    with open(moLogFile,"a") as log:
        log.write("\n" + time.ctime() + ", " + moChange + ", " + userName + ", " + projName + ", " + projDirectory)

def archiveComanche(path):
    """Argument is local output path"""
    from arcpy import env
    import arcpy
    import getpass
    import os
    import time

    exportTime = time.ctime()
    exportTimeElements = exportTime.split(" ")
    formatTime = ""

    for element in exportTimeElements:
        if ":" in element:
            element = element.replace(":","_")
        formatTime = formatTime + "_" + element

    userName = getpass.getuser()
    env.workspace = "C:\\Users\\" + userName + "\\AppData\\Roaming\\ESRI\\Desktop10.0\\ArcCatalog\\Connection to Comanche.sde"

    outputWorkspace = path

    print "Creating New File Geodatabase..."
    arcpy.CreateFileGDB_management(outputWorkspace,"Archive" + formatTime,"10.0")
    outputPath = outputWorkspace + "Archive" + formatTime + ".gdb"
    
    copyFiles = ["TPP_GIS.MCHAMB1.Roadways\\TPP_GIS.MCHAMB1.TXDOT_Roadways","TPP_GIS.MCHAMB1.RTE_CONCURRENT","TPP_GIS.MCHAMB1.RTE_CONTROL_SECTION","TPP_GIS.MCHAMB1.SUBFILES"]
    
    for file in copyFiles:
        if file == "TPP_GIS.MCHAMB1.Roadways\\TPP_GIS.MCHAMB1.TXDOT_Roadways":
            fileName = file.split(".")[4]
            print "Exporting " + fileName
            outFC = outputPath + os.sep + fileName
            arcpy.CopyFeatures_management(file,outFC)
        else:
            fileName = file.split(".")[2]
            print "Exporting " + fileName
            outFC = outputPath + os.sep + fileName
            arcpy.CopyRows_management(file,outFC)

    print "Archive Complete..."
