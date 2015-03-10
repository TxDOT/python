import os, sys

folderRoot = sys.path[0] + os.sep
folders = [ folderRoot + "Geographic Data", folderRoot + "Maps", folderRoot + "PDF", folderRoot + "Script"]

def createFolder(path):
	""" Creates a new folder at the specified path, or a new folder for each path in a list """

	if isinstance(path, basestring):
		if not os.path.exists(path):
			os.makedirs(path)
	elif isinstance(path, list):
		for p in path:
			createFolder(p)
		
	return path

createFolder(folders)