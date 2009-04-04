"""unipath.py - A two-class approach to file/directory operations in Python.

Full usage, documentation, changelog, and history are at
http://sluggo.scrapping.cc/python/unipath/

(c) 2007 by Mike Orr (and others listed in "History" section of doc page).
Permission is granted to redistribute, modify, and include in commercial and
noncommercial products under the terms of the Python license (i.e., the "Python
Software Foundation License version 2" at 
http://www.python.org/download/releases/2.5/license/).
"""

from unipath.abstractpath import AbstractPath
from unipath.path import Path

FSPath = Path

#### FILTER FUNCTIONS (PUBLIC) ####
def DIRS(p):  return p.isdir()
def FILES(p):  return p.isfile()
def LINKS(p):  return p.islink()
def DIRS_NO_LINKS(p):  return p.isdir() and not p.islink()
def FILES_NO_LINKS(p):  return p.isfile() and not p.islink()
def DEAD_LINKS(p):  return p.islink() and not p.exists()
    
