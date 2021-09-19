
import os
import os.path
import shutil
import copy

import file
import data
import triggers

# by Jakub Grzana

tempdir = ".tmp"

def GetTempDir():
    file.EnsureDir(tempdir)
    return tempdir + '/'

def PurgeTempDir():
    file.PurgeDir(tempdir)

#####################################################################################################

NewTemp = dict()

def NewTempEnvAdd(key, data):
    if key in NewTemp:
        raise KeyError(f'{key} already present in New Temp Env')
    NewTemp[key] = data
def NewTempEnvironment():
    return copy.deepcopy(NewTemp)
def GetTempEnvironment(local_env):
    return local_env["temp"]
def OnInit(bot):
    data.NewGuildEnvAdd("temp", NewTempEnvironment())
triggers.OnInitTrigger.append(OnInit)

vessel = None
def PreSave(local_env):
    global vessel
    vessel = local_env["temp"]
    local_env["temp"] = NewTempEnvironment()
def PostSave(local_env):
    global vessel
    local_env["temp"] = vessel
triggers.PreSaveTrigger.append(PreSave)
triggers.PostSaveTrigger.append(PostSave)

#####################################################################################################