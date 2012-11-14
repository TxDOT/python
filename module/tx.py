def updateFile(oldFile, newFile, backupFileFolder,):
	"""Full path to old file, Full path to new file, Full path to backup folder."""
	
	import os, time, shutil
	
	timestamp = str(time.localtime()[2]) + str(time.localtime()[1]) + str(time.localtime()[0]) + "_" + str(time.localtime()[3]) + str(time.localtime()[4]) # Backup timestamp
	backupFile = backupFileFolder + os.sep + oldFile.split("\\")[-1].split(".")[0] + "_" + timestamp + ".py"	# Backup version file path

	shutil.copyfile(oldFile, backupFile)	# Make a backup copy
	shutil.copyfile(newFile, oldFile)		# Replace the old file with the new file

def Checklist(directory):
	"""
	Create a checklist file in "txt" format for any folder - list all files by name.
	"""
	import os
	checkFile = directory + os.sep + 'Checklist.txt'
	dirList = os.listdir(directory)
	for fname in dirList:
		with open(checkFile, "a") as log:
			log.write(str(fname) + "\n")
	print 'Done!'

def Project_Menu():
	"""
	Through a defined menu, allows a user to select a project category, create a new folder, and optionally add a project plan document.
	"""
	import os, shutil, time
#Determine project type and location
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
		path = (r"T:\DATAMGT\MAPPING\Special Maps" + "\\" +tmYR)
	elif ansMenu == '4':
		path = r"T:\DATAMGT\MAPPING\Training"
	else:
		path = raw_input("\nWhat is the filepath of your working directory?\n\nPath: ")	  
#Name the project
	projName = raw_input("\nWhat is the project name?: ")
#Ask for a project plan
	ansPlan = raw_input( "\nWould you like to include a project plan? \n\nY or N: ")
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
	if ansPlan is 'Y':
		shutil.copyfile(projTemp,newProjPlan)
	else:
		pass
	print " "
	projDirectory = (path + "\\" + projName)
	print projDirectory
#Open the file directory in Windows Explorer
	os.startfile(projDirectory)
#Modify or create (if not existing) a general log file for all logged projects
#Change the location of the general log file here:
	logFile = r"T:\\DATAMGT\\MAPPING\\Personal Folders\\David H\\Scripts\\ProjectLogFile.txt"
#Collect user name information
	userName = (os.path.expanduser("~/"))[9:16]
#Record directory creation in general log
	with open(logFile, "a") as log:
		log.write("\n" + time.ctime() + ", " + userName + ", " + projName + ", " + projDirectory)
#Create a log file specifically for minute orders
#Change the location of the Minute Order log file here:
	moLogFile = r"T:\\DATAMGT\\MAPPING\\Personal Folders\\David H\\Scripts\\MinuteOrderProjectLogFile.txt"
#Log minute order specifics into Minute Order log file
	with open(moLogFile, "a") as log:
		log.write("\n" + time.ctime() + ", " + moChange + ", " + userName + ", " + projName + ", " + projDirectory)
