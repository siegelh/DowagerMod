# -*- coding: utf-8 -*-
"""
Created on Tue May 19 21:01:47 2015

@author: Harrison
"""

import sys
import distutils.dir_util as dis
import winsound

version = '0.1.0'
print('Preparing to install HarrisonMod version %s, please wait...' % version)
winsound.PlaySound('install_noise.wav',winsound.SND_FILENAME)

src_path = sys.argv[0][:-16].replace('/','\\') + 'assets'
civ_path = input('Type the path to where Civ Beyond the Sword is installed (ex: C:\Program Files (x86)\Steam\SteamApps\common\): ').replace("\n",'\\') + "\\Sid Meier's Civilization IV Beyond the Sword\\Beyond the Sword\\Assets"

dis.copy_tree(src_path,civ_path)
print('Finished installing HarrisonMod version %s!' % version)
exit = input('Click enter to exit setup.')
              
           