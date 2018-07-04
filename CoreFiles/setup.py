# -*- coding: utf-8 -*-
"""
Created on Tue May 19 21:57:07 2015

@author: Harrison
"""

from distutils.core import setup
import py2exe

setup(console=['install.py'])

"""
import sys
from cx_Freeze import setup, Executable

setup(
    name = "DowagerMod",
    version = "0.2.1",
    description = "You know golly well what this is.",
    executables = [Executable("install.py", base = "Win32GUI")])
	"""