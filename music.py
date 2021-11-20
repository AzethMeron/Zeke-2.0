
import random
import os
import os.path
import threading
from multiprocessing import Process
from multiprocessing import Queue
import datetime

import tools
import file
import temp
import data
import triggers
import cmd
import log

# Youtube video urls, used for checking status
# THEY MUST BE SHORT AND AVAILABLE. Also more than 3 is overkill and harmful one
testing_urls = ["https://youtu.be/07RVnTrRDAo", "https://youtu.be/WI1CqmWSjgQ", "https://youtu.be/dQw4w9WgXcQ"] 

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

# Note:
# temp_env["music_player"] and temp_env["music_loop"] should be remade
# instead of direct access, GetMusicPlayer(temp_env) and SetMusicPlayer(temp_env) functions should be used
# Current code works so i'm not going to prioretize it tho. Maybe when i'll decide to add smt here, i'll remake it

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
            if QueueLength(temp_env) == 0:
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
    with lock:
        random.shuffle(GetMusicQueue(temp_env))

def Clear(temp_env):
    lock = GetMusicLock(temp_env)
    with lock:
        GetMusicQueue(temp_env).clear()
    
def Remove(temp_env, index):
    lock = GetMusicLock(temp_env)
    feedback = False
    with lock:
        if index >= 0 and index < len(GetMusicQueue(temp_env)):
            GetMusicQueue(temp_env).pop(index)
            feedback = True
    return feedback
    
def Fetch(temp_env):
    local_queue = GetMusicQueue(temp_env)
    lock = GetMusicLock(temp_env)
    output = None
    with lock:
        if len(local_queue) > 0:
            output = local_queue.pop(0)
            if temp_env["music_loop"]: local_queue.append(output)
    return output

def QueueLength(temp_env):
    local_queue = GetMusicQueue(temp_env)
    lock = GetMusicLock(temp_env)
    output = None
    with lock:
        output = len(local_queue)
    return output

def AddSongs(temp_env, objs, first):
    if first: objs.reverse()
    lock = GetMusicLock(temp_env)
    with lock:
        try:
            for obj in objs:
                if first: GetMusicQueue(temp_env).insert(0, obj)
                else: GetMusicQueue(temp_env).append(obj)
                VidQueue.put(obj)
        except Exception as e:
            log.write(e)

################################################################################

# Here goes pytube 

import pytube
import discord

def AudioSource(filepath):
    return discord.FFmpegPCMAudio(filepath)

def GetAudio(obj, dir): # obj - YouTube object
    try:
        filename = tools.Hash(GetTitle(obj))
        if file.ExistInDir(dir, filename):
            return os.path.join(dir, filename)
        streams = obj.streams
        stream = streams.filter(type='audio').get_audio_only()
        stream.download(output_path=dir, filename=filename, max_retries=10)
        PreprocessAudio(dir, filename)
        return os.path.join(dir, filename)
    except:
        return None

async def youtubeStatus():
    for url in testing_urls:
        obj = pytube.YouTube(url)
        if GetAudio(obj, GetMusicDir()): return True
    return False
triggers.Status.append( ("Music bot's youtube integration", youtubeStatus) )

def CheckVideo(obj):
    return None # Validating is slow, too slow for big playlists, and besides... why restrict private bot
    try:
        obj.check_availability()
        streams_check = obj.streams
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
        if "list" in url: # playlist
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
    
def DescribeObj(obj):
    try:
        title = GetTitle(obj)
        duration = GetDuration(obj)
        return f'{title} [{duration}]'
    except Exception as e:
        return f'ERROR DURING PROCESSING {str(e)}'
    
class Player:
    def internal_play(self, err):
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
                self.voice.play(AudioSource(filepath), after=self.internal_play)
            else:
                self.internal_play(None)
    def play(self, err):
        self.voice.play(AudioSource("ZQUIET.WAV"), after=self.internal_play)
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

async def user_feedback(ctx, objs, failed):
    if len(failed) == 1:
        message  = "Failed to play video: " + DescribeObj(failed[0][0]) + " REASON: " + failed[0][1]
        await ctx.message.reply("```" + message + "```")
        return True
    elif len(objs) == 1:
        message = "Played: " + DescribeObj(objs[0])
        await ctx.message.reply("```" + message + "```")
        return True
    return False

async def play(ctx, args, first):
    local_env = data.GetGuildEnvironment(ctx.guild)
    temp_env = temp.GetTempEnvironment(local_env)
    voice = await connect(temp_env, ctx, temp_env["music_player"])
    (objs, failed) = ProcessInput(args)
    feedback = await user_feedback(ctx, objs, failed)
    AddSongs(temp_env, objs, first)
    run_player(voice, temp_env)
    return feedback

async def cmd_play(ctx, args):
    return await play(ctx, args, False)

async def cmd_insert(ctx, args):
    return await play(ctx, args, True)

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

def queue_header(temp_env):
    output = f"CURRENT QUEUE [Looping: {temp_env['music_loop']}]\n"
    if temp_env["music_player"]:
        currently_playing = temp_env["music_player"].currently_playing()
        if currently_playing:
            output = output + "Currently playing: " + DescribeObj(currently_playing) + "\n"
    return output

async def cmd_queue(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    temp_env = temp.GetTempEnvironment(local_env)
    output = queue_header(temp_env)
    lock = GetMusicLock(temp_env)
    with lock:
        queue = GetMusicQueue(temp_env)
        (num_min, num_max) = tools.list_size_args(args, queue, 0, 5)
        for i in range(num_min, num_max):
            output = output + f'{i+1}. ' + DescribeObj(queue[i]) + '\n'
        if len(queue) > num_max:
            output = output + f'...{len(queue)}\n'
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

cmd.Add(triggers.parser, "music", parser, "Music bot feature", "")

################################################################################
