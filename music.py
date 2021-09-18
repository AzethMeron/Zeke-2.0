
import file
import temp
import data
import random
import pytube
import triggers
import cmd

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
VidQueue = Queue()
VidProcesses = []
ProcNum = 4

def PreSave(local_env):
    global vessel
    vessel = local_env["music_queue"]
    local_env["music_queue"] = []
triggers.PreSaveTrigger.append(PreSave)

def PostSave(local_env):
    global vessel
    local_env["music_queue"] = vessel
triggers.PostSaveTrigger.append(PostSave)

def OnInit(bot):
    global VidQueue, VidProcesses, ProcNum
    for i in range(0,ProcNum): 
        VidProcesses.append( Process(target=ProcessFunction, args=(VidQueue,)) )
        VidProcesses[-1].start()
triggers.OnInitTrigger.append(OnInit)

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

## Function that is called by subprocesses
def ProcessFunction(queue):
    while True:
        obj = queue.get()
        DownloadAudio(obj, GetMusicDir())

################################################################################

async def connect(ctx):
    voice = ctx.author.voice
    channel = voice.channel
    await channel.connect()

async def play(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    url = args.pop(0)
    obj = pytube.YouTube(url)
    local_env["music_queue"].append(obj)
    VidQueue.put(obj)
    return (True, None)

################################################################################

parser = cmd.Parser()
cmd.Add(parser, "play", play)

async def command(ctx, args):
    await cmd.Parse(parser, ctx, args)

################################################################################
