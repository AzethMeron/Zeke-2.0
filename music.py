
import random
import os
import os.path
import threading
from multiprocessing import Process
from multiprocessing import Queue

import tools
import file
import temp
import data
import triggers
import cmd

# uses pytube to download audio from youtube videos
# and ffmpeg to process/play it
# "music_queue" stores pytube.YouTube objects, however it is abstracted so switching to smt else like url shouldn't be too problematic
# Discord uses multi-threading to play audio, thus "music_queue" is protected by lock (mutex)
# Don't edit "music_queue" manually, use only abstract tools!

################################################################################

music_dir = "music"
temp.NewTempEnvAdd("music_queue", [])
temp.NewTempEnvAdd("music_lock", None)
temp.NewTempEnvAdd("music_player", None)

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

## Function that is called by subprocesses (downloading audio streams)
def ProcessFunction(queue):
    while True:
        obj = queue.get()
        GetAudio(obj, GetMusicDir())

################################################################################

# Abstract tools

def GetMusicDir():
    out = temp.GetTempDir() + music_dir
    try:
        file.EnsureDir(out)
    except:
        pass
    return out + "/"

def GetMusicQueue(temp_env):
    return temp_env["music_queue"]

def GetMusicLock(temp_env):
    if not temp_env["music_lock"]:
        temp_env["music_lock"] = threading.Lock()
    return temp_env["music_lock"]

def PreprocessAudio(dir, filename):
    return None

def Shuffle(temp_env):
    lock = GetMusicLock(temp_env)
    lock.acquire()
    random.shuffle(GetMusicQueue(temp_env))
    lock.release()

def Fetch(temp_env):
    local_queue = GetMusicQueue(temp_env)
    lock = GetMusicLock(temp_env)
    output = None
    lock.acquire()
    if len(local_queue) > 0:
        output = local_queue.pop(0)
    lock.release()
    return output

def AddSongs(temp_env, objs):
    lock = GetMusicLock(temp_env)
    lock.acquire()
    try:
        for obj in objs:
            GetMusicQueue(temp_env).append(obj)
            VidQueue.put(obj)
    except Exception as e:
        print(e)
    lock.release()

################################################################################

# Here goes pytube 

import pytube
import discord

def AudioSource(filepath):
    return discord.FFmpegPCMAudio(filepath)

def GetAudio(obj, dir): # obj - YouTube object
    filename = tools.Hash(obj.title)
    if filename in file.ListOfFiles(dir):
        return os.path.join(dir, filename)
    streams = obj.streams
    stream = streams.filter(type='audio').get_audio_only()
    stream.download(output_path=dir, filename=filename, max_retries=10)
    PreprocessAudio(dir, filename)
    return os.path.join(dir, filename)

def ProcessInput(args): # len(args) >= 1, guaranteed
    # function to convert list of arguments into list of pytube.YouTube objects
    objs = []
    if tools.is_url(args[0]):
        url = args.pop(0)
        if "playlist" in url: # playlist
            objs = [ obj for obj in pytube.Playlist(url).videos ]
        else: # single video
            objs = [ pytube.YouTube(url) ]
    else:
        title = ' '.join(args)
        results = pytube.Search(title).results
        objs = [ results[0] ]
    return objs

class Player:
    def play(self, err):
        obj = Fetch(self.env)
        if obj:
            filepath = GetAudio(obj, GetMusicDir())
            self.voice.play(AudioSource(filepath), after=self.play)
    def __init__(self, voice, temp_env):
        self.voice = voice
        self.env = temp_env
        self.play(None)

################################################################################

# Commands

async def connect(temp_env, ctx):
    voice = ctx.author.voice
    channel = voice.channel
    return await channel.connect()

async def play(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    temp_env = temp.GetTempEnvironment(local_env)
    if len(args) < 1: raise RuntimeError("You forgot to mention anything to be played")
    voice = await connect(temp_env, ctx)
    AddSongs(temp_env, ProcessInput(args))
    temp_env["music_player"] = Player(voice, temp_env)

################################################################################

# parser

parser = cmd.Parser()
cmd.Add(parser, "play", play, "play music by name, url or playlist url")

async def command(ctx, args):
    await cmd.Parse(parser, ctx, args)

################################################################################
