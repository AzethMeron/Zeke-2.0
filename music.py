
import random
import pytube
import os
import os.path
import threading
from multiprocessing import Process
from multiprocessing import Queue
import discord

import tools
import file
import temp
import data
import triggers
import cmd

################################################################################

music_dir = "music"
temp.NewTempEnvAdd("music_queue", [])
temp.NewTempEnvAdd("queue_lock", None)

################################################################################

VidQueue = Queue()
VidProcesses = []
ProcNum = 4

def OnInit(bot):
    global VidQueue, VidProcesses, ProcNum
    for i in range(0,ProcNum): 
        VidProcesses.append( Process(target=ProcessFunction, args=(VidQueue,)) )
        VidProcesses[-1].start()
triggers.OnInitTrigger.append(OnInit)

def OnPurge(local_env):
    queue = GetMusicQueue(local_env)
    for obj in queue:
        VidQueue.put(obj)
triggers.PostTempPurge.append(OnPurge)

################################################################################

def GetMusicDir():
    out = temp.GetTempDir() + music_dir
    try:
        file.EnsureDir(out)
    except:
        pass
    return out + "/"

def GetMusicQueue(local_env):
    return temp.GetTempEnvironment(local_env)["music_queue"]

def GetMusicLock(local_env):
    if not temp.GetTempEnvironment(local_env)["queue_lock"]:
        temp.GetTempEnvironment(local_env)["queue_lock"] = threading.Lock()
    return temp.GetTempEnvironment(local_env)["queue_lock"]

def GetAudio(obj, dir): # obj - YouTube object
    filename = tools.Hash(obj.title)
    if filename in file.ListOfFiles(dir):
        return os.path.join(dir, filename)
    streams = obj.streams
    stream = streams.filter(type='audio').get_audio_only()
    stream.download(output_path=dir, filename=filename, max_retries=10)
    PreprocessAudio(dir, filename)
    return os.path.join(dir, filename)

def AudioSource(filepath):
    return discord.FFmpegPCMAudio(filepath)

def PreprocessAudio(dir, filename):
    return None

def Shuffle(local_env):
    random.shuffle(GetMusicQueue(local_env))

def Fetch(local_env):
    local_queue = GetMusicQueue(local_env)
    if len(local_queue) > 0:
        return local_queue.pop(0)
    return None

def AddSong(local_env, url):
    obj_list = []
    if "playlist" in url:
        obj_list = [ vid for vid in pytube.Playlist(url).videos ]
    else:
        obj_list = [ pytube.YouTube(url) ]
    for obj in obj_list:
        GetMusicQueue(local_env).append(obj)
        VidQueue.put(obj)

################################################################################

## Function that is called by subprocesses (downloading audio streams)
def ProcessFunction(queue):
    while True:
        obj = queue.get()
        GetAudio(obj, GetMusicDir())

################################################################################

class Player:
    def play(self, err):
        obj = Fetch(self.env)
        if obj:
            filepath = GetAudio(obj, GetMusicDir())
            self.voice.play(AudioSource(filepath), after=self.play)
    def __init__(self, voice, local_env):
        self.voice = voice
        self.env = local_env
        self.play(None)

async def connect(ctx):
    voice = ctx.author.voice
    channel = voice.channel
    return await channel.connect()

async def play(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    url = args.pop(0) 
    AddSong(local_env, url)
    voice = await connect(ctx)
    player = Player(voice, local_env)
    return (True, None)

################################################################################

parser = cmd.Parser()
cmd.Add(parser, "play", play, "play music by name, url or playlist url")

async def command(ctx, args):
    await cmd.Parse(parser, ctx, args)

################################################################################
