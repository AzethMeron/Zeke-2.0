
import random
import os
import os.path
import threading
from multiprocessing import Process
from multiprocessing import Queue
import traceback
import datetime

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
temp.NewTempEnvAdd("music_loop", False)

################################################################################

VidQueue = Queue()
VidProcesses = []
ProcNum = 4

def OnInit(bot):
    global VidQueue, VidProcesses, ProcNum
    for i in range(0,ProcNum): 
        VidProcesses.append( Process(target=DownloaderProcess, args=(VidQueue,)) )
        VidProcesses[-1].start()
triggers.OnInitTrigger.append(OnInit)

def OnPurge(local_env):
    queue = GetMusicQueue(temp.GetTempEnvironment(local_env))
    for obj in queue:
        VidQueue.put(obj)
triggers.PostTempPurge.append(OnPurge)

async def EachMinute(bot, local_env, guild, minute):
    temp_env = temp.GetTempEnvironment(local_env)
    if temp_env["music_player"]:
        if len(temp_env["music_player"].voice.channel.voice_states.keys()) <= 1:
            await stop_player(temp_env)
            Clear(temp_env)
        elif not temp_env["music_player"].is_playing():
            await stop_player(temp_env)
    return None
triggers.Timers.append( (1, EachMinute) )

## Function that is called by subprocesses (downloading audio streams)
def DownloaderProcess(queue):
    while True:
        obj = queue.get()
        GetAudio(obj, GetMusicDir())

################################################################################

# Abstract tools

def GetMusicDir():
    out = temp.GetTempDir() + music_dir
    file.EnsureDir(out)
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

def Clear(temp_env):
    lock = GetMusicLock(temp_env)
    lock.acquire()
    GetMusicQueue(temp_env).clear()
    lock.release()
    
def Remove(temp_env, index):
    lock = GetMusicLock(temp_env)
    lock.acquire()
    feedback = False
    if index >= 0 and index < len(GetMusicQueue(temp_env)):
        GetMusicQueue(temp_env).pop(index)
        feedback = True
    lock.release()
    return feedback
    
def Fetch(temp_env):
    local_queue = GetMusicQueue(temp_env)
    lock = GetMusicLock(temp_env)
    output = None
    lock.acquire()
    if len(local_queue) > 0:
        output = local_queue.pop(0)
        if temp_env["music_loop"]: local_queue.append(output)
    lock.release()
    return output

def AddSongs(temp_env, objs, first):
    if first: objs.reverse()
    lock = GetMusicLock(temp_env)
    lock.acquire()
    try:
        for obj in objs:
            if first: GetMusicQueue(temp_env).insert(0, obj)
            else: GetMusicQueue(temp_env).append(obj)
            VidQueue.put(obj)
    except Exception as e:
        print(traceback.format_exc())
    lock.release()

################################################################################

# Here goes pytube 

import pytube
import discord

def AudioSource(filepath):
    return discord.FFmpegPCMAudio(filepath)

def GetAudio(obj, dir): # obj - YouTube object
    try:
        filename = tools.Hash(GetTitle(obj))
        if filename in file.ListOfFiles(dir):
            return os.path.join(dir, filename)
        streams = obj.streams
        stream = streams.filter(type='audio').get_audio_only()
        stream.download(output_path=dir, filename=filename, max_retries=10)
        PreprocessAudio(dir, filename)
        return os.path.join(dir, filename)
    except:
        return None

def CheckVideo(obj):
    return None # Validating is slow, too slow for big playlists, and besides... why restrict private bot
    try:
        obj.check_availability()
        if obj.length > (60*60+5): raise RuntimeError("Cannot play video longer than 1 hour")
    except Exception as e:
        return e
    return None

def ValidateVideo(obj, successful, failed):
    result = CheckVideo(obj)
    if result: 
        failed.append( (obj, str(result)) )
    else:
        successful.append(obj)

def ProcessInput(args): 
    # function to convert list of arguments into list of pytube.YouTube objects
    objs = []
    failed = []
    if len(args) == 0:
        return ([], [])
    if tools.is_url(args[0]):
        url = args.pop(0)
        if "playlist" in url: # playlist
            for obj in pytube.Playlist(url).videos:
                ValidateVideo(obj, objs, failed)
        else: # single video
            obj = pytube.YouTube(url)
            ValidateVideo(obj, objs, failed)
    else:
        title = ' '.join(args)
        obj = pytube.Search(title).results[0]
        ValidateVideo(obj, objs, failed)
    return (objs, failed)

def GetTitle(obj):
    return obj.title

def GetDuration(obj): # in string, this isn't raw seconds length!
    return str(datetime.timedelta(seconds=obj.length))
    
class Player:
    def play(self, err):
        self.currently = None
        self.skip_voting = 0
        self.voters = set()
        if self.stop_sign:
            return False
        obj = Fetch(self.env)
        if obj:
            filepath = GetAudio(obj, GetMusicDir())
            if filepath:
                self.currently = obj
                self.voice.play(AudioSource(filepath), after=self.play)
            else:
                self.play(None)
    def is_playing(self):
        return self.voice.is_playing()
    def stop(self):
        self.stop_sign = True
        self.skip()
    def skip(self):
        self.voice.stop()
    def vote_skip(self, user):
        if tools.Hash(user.id) not in self.voters: 
            self.skip_voting = self.skip_voting + 1
            self.voters.add(tools.Hash(user.id))
        num = len(self.voice.channel.voice_states.keys())
        val = round(num/2) - self.skip_voting
        if val <= 0:
            self.skip()
            return None
        return val
    def currently_playing(self):
        return self.currently
    def __init__(self, voice, temp_env):
        self.voice = voice
        self.env = temp_env
        self.currently = None
        self.skip_voting = 0
        self.voters = set()
        self.stop_sign = False
        self.play(None)

################################################################################

# Command tools

async def stop_player(temp_env):
    temp_env["music_player"].stop()
    await temp_env["music_player"].voice.disconnect()
    temp_env["music_player"] = None

async def connect(temp_env, ctx, player):
    voice = ctx.author.voice
    if not voice: raise RuntimeError("You must be in voice channel to play music")
    channel = voice.channel
    if player:
        bot_channel = player.voice.channel
        if bot_channel.id == channel.id: return player.voice
        raise RuntimeError("You must be in the same channel as bot to use that command")
    return await channel.connect()

def check_channels(ctx, player):
    voice = ctx.author.voice
    if not voice: return False
    channel = voice.channel
    if not player: return False
    bot_channel = player.voice.channel
    if bot_channel.id != channel.id: return False
    return True

def check_permissions(ctx):
    perms = ctx.message.author.guild_permissions
    return perms.manage_channels

def run_player(voice, temp_env):
    if temp_env["music_player"]:
        if not temp_env["music_player"].is_playing():
            temp_env["music_player"].play(None)
    else:
        temp_env["music_player"] = Player(voice, temp_env)

################################################################################

async def play(ctx, args, first):
    local_env = data.GetGuildEnvironment(ctx.guild)
    temp_env = temp.GetTempEnvironment(local_env)
    voice = await connect(temp_env, ctx, temp_env["music_player"])
    (objs, failed) = ProcessInput(args)
    AddSongs(temp_env, objs, first)
    run_player(voice, temp_env)

async def cmd_play(ctx, args):
    await play(ctx, args, False)

async def cmd_insert(ctx, args):
    await play(ctx, args, True)

async def cmd_skip(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    temp_env = temp.GetTempEnvironment(local_env)
    player = temp_env["music_player"]
    if not check_channels(ctx, player): raise RuntimeError("You must be in the same channel as bot to use that command")
    result = player.vote_skip(ctx.author)
    if result != None:
        raise RuntimeWarning("Need more people to skip: " + str(result))

async def cmd_fskip(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    temp_env = temp.GetTempEnvironment(local_env)
    player = temp_env["music_player"]
    if not check_channels(ctx, player): raise RuntimeError("You must be in the same channel as bot to use that command")
    if not check_permissions(ctx): raise RuntimeError("Insufficent permissions")
    player.skip()

async def cmd_shuffle(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    temp_env = temp.GetTempEnvironment(local_env)
    if not check_channels(ctx, temp_env["music_player"]): raise RuntimeError("You must be in the same channel as bot to use that command")
    Shuffle(temp_env)

async def cmd_clear(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    temp_env = temp.GetTempEnvironment(local_env)
    if not check_channels(ctx, temp_env["music_player"]): raise RuntimeError("You must be in the same channel as bot to use that command")
    if not check_permissions(ctx): raise RuntimeError("Insufficent permissions")
    Clear(temp_env)

async def cmd_stop(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    temp_env = temp.GetTempEnvironment(local_env)
    if not check_channels(ctx, temp_env["music_player"]): raise RuntimeError("You must be in the same channel as bot to use that command")
    if not check_permissions(ctx): raise RuntimeError("Insufficent permissions")
    await stop_player(temp_env)

async def cmd_queue(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    temp_env = temp.GetTempEnvironment(local_env)
    num_min = 0
    num_max = 5
    if len(args) == 1:
        if int(args[0]) < 1: raise RuntimeError("Funny")
        num_max = int(args[0])
    if len(args) == 2:
        if int(args[0]) < 1: raise RuntimeError("Funny")
        if int(args[0]) > int(args[1]): raise RuntimeError("Funny")
        num_min = int(args[0]) - 1
        num_max = int(args[1])
    output = f"CURRENT QUEUE [Looping: {temp_env['music_loop']}]\n"
    if temp_env["music_player"]:
        currently_playing = temp_env["music_player"].currently_playing()
        if currently_playing:
            output = output + "Currently playing: " + GetTitle(currently_playing) + f" [{GetDuration(currently_playing)}]\n"
    lock = GetMusicLock(temp_env)
    lock.acquire()
    queue = GetMusicQueue(temp_env)
    num_max = min(num_max,len(queue))
    for i in range(num_min, num_max):
        try:
            title = GetTitle(queue[i])
            duration = GetDuration(queue[i])
            output = output + f'{i+1}. {title} [{duration}]\n'
        except Exception as e:
            output = output + f'{i+1}. ERROR DURING PROCESSING {str(e)}\n'
    if len(queue) > num_max:
        output = output + f'...{len(queue)}\n'
    lock.release()
    for out in tools.segment_text(output, 1980):
        await ctx.message.reply("```" + out + "```")
    return True

async def cmd_remove(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    temp_env = temp.GetTempEnvironment(local_env)
    if not check_channels(ctx, temp_env["music_player"]): raise RuntimeError("You must be in the same channel as bot to use that command")
    if not check_permissions(ctx): raise RuntimeError("Insufficent permissions")
    if len(args) != 1: raise RuntimeError("incorrect arguments")
    index = int(args[0]) - 1
    if not Remove(temp_env, index): raise ValueError("Incorrect index")

async def cmd_loop(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    temp_env = temp.GetTempEnvironment(local_env)
    if not check_permissions(ctx): raise RuntimeError("Insufficent permissions")
    if len(args) == 0:
        temp_env["music_loop"] = not temp_env["music_loop"]
        await ctx.message.reply(f"Looping: {temp_env['music_loop']}") 
        return True
    else:
        if args[0] == "enabled":
            temp_env["music_loop"] = True
        elif args[0] == "disabled":
            temp_env["music_loop"] = False
        else:
            await ctx.message.reply(f"Incorrect argument {args[0]}, expected: enabled/disabled") 
            return True

################################################################################

# parser

parser = cmd.Parser()
cmd.Add(parser, "play", cmd_play, "play music by name, url or playlist url", "dummy")
cmd.Add(parser, "skip", cmd_skip, "skip currently playing track", "dummy")
cmd.Add(parser, "fs", cmd_fskip, "skip currently playing track (without voting)", "dummy")
cmd.Add(parser, "shuffle", cmd_shuffle, "shuffle queue", "dummy")
cmd.Add(parser, "clear", cmd_clear, "clear queue", "dummy")
cmd.Add(parser, "stop", cmd_stop, "stops playing", "dummy")
cmd.Add(parser, "insert", cmd_insert, "play music, inserting it at beginning of queue", "dummy")
cmd.Add(parser, "queue", cmd_queue, "display queue", "dummy")
cmd.Add(parser, "remove", cmd_remove, "remove music from queue", "dummy")
cmd.Add(parser, "loop", cmd_loop, "enable/disable looping of queue", "dummy")

async def command(ctx, args):
    return await cmd.Parse(parser, ctx, args)

################################################################################
