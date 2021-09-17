
import file
import temp
import data
import random
import pytube

import os
import os.path

from multiprocessing import Process
from multiprocessing import Queue

################################################################################

music_dir = "music"
data.NewGuildEnvAdd("music_queue", [])

################################ SAVE SUPPORT ##################################
## Youtube music queue shouldn't be stored in database

vessel = None

def PreSave(local_env):
    vessel = local_env["music_queue"]
    local_env["music_queue"] = []
data.PreSaveTrigger.append(PreSave)

def PostSave(local_env):
    local_env["music_queue"] = vessel
data.PostSaveTrigger.append(PostSave)

def OnInit(bot):
    return None

################################################################################

def GetMusicDir():
    out = temp.GetTempDir() + music_dir
    file.EnsureDir(out)
    return out + "/"

def GetMusicQueue(local_env):
    return local_env["music_queue"]

def DownloadAudio(obj, dir): # obj - YouTube object
    filename = file.HashName(' ' + obj.title)
    if filename in file.ListOfFiles(dir):
        return os.path.join(dir, filename)
    streams = obj.streams
    stream = streams.filter(type='audio').get_audio_only()
    stream.download(output_path=dir, filename=filename, max_retries=10)
    return os.path.join(dir, filename)

def Shuffle(local_env):
    random.shuffle(GetMusicQueue(local_env))

def Fetch(local_env):
    local_queue = GetMusicQueue(local_env)
    if len(local_queue) > 0:
        return local_queue.pop(0)
    return None

################################################################################
