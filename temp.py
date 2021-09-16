
import os
import os.path
import shutil
import file

# by Jakub Grzana

tempdir = ".tmp"

def GetTempDirPath():
    file.EnsureDir(tempdir)
    return tempdir + '/'

def PurgeTempDir():
    file.PurgeDir(tempdir)