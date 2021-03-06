
import os
import os.path
import shutil
import copy

import log
import tools
import file
import data
import triggers

# by Jakub Grzana

tempdir = ".tmp"

def GetTempDir():
    file.EnsureDir(tempdir)
    return tempdir + '/'

def PurgeTempDir(bot):
    file.PurgeDir(tempdir)
    for guild in bot.guilds:
        local_env = data.GetGuildEnvironment(guild)
        for func in triggers.PostTempPurge: 
            try:
                func(local_env)
            except Exception as e:
                log.write(e)

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
data.NewGuildEnvAdd("temp", NewTemp) # it is reference, not deepcopy - feature, not bug

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