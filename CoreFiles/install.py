# -*- coding: utf-8 -*-
"""
Created on Tue May 19 21:01:47 2015

@author: Harrison
"""

import sys
import distutils.dir_util as dis
import winsound

version = '0.2.1'
print('Preparing to install HarrisonMod version %s, please wait...' % version)
winsound.PlaySound('install_noise.wav',winsound.SND_FILENAME)

## Functions
def findPath(civ_drive):
"""
Returns either the path where Civ 4 is installed or 'Failed'.
"""
	for root, directories, filenames in os.walk(civ_path.upper() + ':\\Program Files (x86)')
		for directory in directories:
			print(os.path.join(root, directory))
			current_path = os.path.join(root, directory).replace("\n",'\\')
			if current_path.contains("\\Sid Meier's Civilization IV Beyond the Sword\\Beyond the Sword\\Assets"):
				print("""
				---------------------------------
				Civ 4 BTS Assets Directory found!
				---------------------------------
				
				{0}
				
				""".format(current_path)
				response = input("Is this the correct directory? [y / n]: ")
				response = response.lower()
				if response == "y":
					return current_path
				else:
					pass
	return "Failed"
								
def installMod(civ_directory):
	dis.copy_tree(src_path,civ_path)
	print('Finished installing HarrisonMod version %s!' % version)

## Fetch install path
src_path = sys.argv[0][:-16].replace('/','\\') + 'assets'
civ_drive = input('Type the letter drive name (caps insensitive) where Civ Beyond the Sword is installed: ')
civ_path = findPath(civ_drive)
if civ_path == "Failed":
	print("Could not find Assets directory. Installation failed. Goodbye!")
else:
	print("""
	
	Installing DowagerMod to {0}
	
	""".current_path)
	installMod(civ_path)
	exit = input('Success! Click enter to exit setup.')
              
           