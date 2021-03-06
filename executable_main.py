#!/usr/bin/env python

import os
import discord # Discord API
from discord.ext import tasks
from discord.ext import commands
from dotenv import load_dotenv # ENV vars
from discord.ext.commands import has_permissions, MissingPermissions, CommandNotFound
from datetime import datetime, timedelta

# TOOLS
import tools
import file
import temp
import data
import cmd
import triggers
import debug
import log
import storage
import aes

# FEATURES
import music
import welcome
import translate
#import rand # temporarily removed
import mode
import levels
import text_ai
import reaction_roles
import reactionary
import lurker
import dm_responder
import mention_responder
import vademecum

# LOADING BUNDLE
import bundle

load_dotenv() # load environmental variables from file .env
intents = discord.Intents.default()
intents.members = True
DiscordClient = commands.Bot(command_prefix="unused",intents=intents) # create client of discord-bot
VERSION = "2.0"
REPO_LINK = "https://github.com/AzethMeron/Zeke-2.0"

#################################### TIMER #####################################

PURGE_DIR_INTERVAL_MIN = int(os.getenv('PURGE_DIR_INTERVAL_MIN')) if os.getenv('PURGE_DIR_INTERVAL_MIN') else 6*60
DATA_SAVE_INTERVAL_MIN = int(os.getenv('DATA_SAVE_INTERVAL_MIN')) if os.getenv('DATA_SAVE_INTERVAL_MIN') else 60

minute = 1
@tasks.loop(minutes=1)
async def each_minute():
    global minute
    if minute % (PURGE_DIR_INTERVAL_MIN) == 0:
        temp.PurgeTempDir(DiscordClient)
    if minute % (DATA_SAVE_INTERVAL_MIN) == 0:
        for guild in DiscordClient.guilds: data.SaveGuildEnvironment(guild)
    await TimerTick(minute, DiscordClient)
    minute = (minute + 1) % 100000

async def TimerTick(minute, DiscordClient):
    for (m,func) in triggers.Timers:            
        if abs(minute) % m == 0:
            for guild in DiscordClient.guilds:
                local_env = data.GetGuildEnvironment(guild)
                try:
                    await func(DiscordClient, local_env, guild, minute)
                except Exception as e:
                    log.write(e)

################################################################################

################################### ERROR ######################################

@DiscordClient.event
async def on_error(event, *args, **kwargs):
    print("UNHANDLED EXCEPTION")
    print(event)
    log.write(RuntimeError("on_error event"))

################################################################################

############################## DISCORD TRIGGERS ################################

@DiscordClient.event
async def on_message(message):
    if message.author.bot: return
    if not message.guild: # Not in guild, so DM
        for func in triggers.on_dm:
            try:
                await func(message)
            except Exception as e:
                log.write(e)
        return
    normalised = tools.EnsureEnglish(message.content)
    local_env = data.GetGuildEnvironment(message.guild)
    try:
        await cmd.ProcessCommands(local_env, message, DiscordClient)
    except Exception as e:
        log.write(e)
    for func in triggers.on_message: 
        try:
            await func(local_env, message, normalised)
        except Exception as e:
            log.write(e)

@DiscordClient.event
async def on_reaction_add(reaction, user):
    if user.bot: return 
    if not reaction.message.guild: return
    local_env = data.GetGuildEnvironment(reaction.message.guild)
    for func in triggers.on_reaction_add: 
        try:
            await func(local_env, reaction, user)
        except Exception as e:
            log.write(e)

@DiscordClient.event        
async def on_reaction_remove(reaction, user):
    if user.bot: return
    if not reaction.message.guild: return
    local_env = data.GetGuildEnvironment(reaction.message.guild)
    for func in triggers.on_reaction_remove: 
        try:
            await func(local_env, reaction, user)
        except Exception as e:
            log.write(e)

@DiscordClient.event
async def on_raw_reaction_add(payload):
    if not payload.guild_id: return
    guild = DiscordClient.get_guild(payload.guild_id)
    local_env = data.GetGuildEnvironment(guild)
    member = guild.get_member(payload.user_id)
    if member.bot: return
    emoji = payload.emoji
    message = await guild.get_channel(payload.channel_id).fetch_message(payload.message_id)
    for func in triggers.raw_reaction_add: 
        try:
            await func(payload, local_env, emoji, member, guild, message)
        except Exception as e:
            log.write(e)

@DiscordClient.event
async def on_raw_reaction_remove(payload):
    if not payload.guild_id: return
    guild = DiscordClient.get_guild(payload.guild_id)
    local_env = data.GetGuildEnvironment(guild)
    member = guild.get_member(payload.user_id)
    if member.bot: return
    emoji = payload.emoji
    message = await guild.get_channel(payload.channel_id).fetch_message(payload.message_id)
    for func in triggers.raw_reaction_remove: 
        try:
            await func(payload, local_env, emoji, member, guild, message)
        except Exception as e:
            log.write(e)

@DiscordClient.event
async def on_member_join(member):
    local_env = data.GetGuildEnvironment(member.guild)
    for func in triggers.on_member_join: 
        try:
            await func(local_env, member)
        except Exception as e:
            log.write(e)

@DiscordClient.event
async def on_member_remove(member):
    local_env = data.GetGuildEnvironment(member.guild)
    for func in triggers.on_member_remove: 
        try:
            await func(local_env, member)
        except Exception as e:
            log.write(e)

@DiscordClient.event
async def on_guild_join(guild):
    local_env = data.GetGuildEnvironment(guild)
    output = f"Why hello there! I'm Zeke, version {VERSION}\nI'm open source bot: {REPO_LINK}\nMy only duty is to serve you, in a number of ways:\n"
    for func in triggers.on_guild_join:
        try:
            result = await func(local_env, guild)
            if result:
                output = output + result + "\n"
        except Exception as e:
            log.write(e)
    output = output + f'Try using "{cmd.PREFIX} help".'
    try:
        channel = guild.system_channel
        if channel:
            for out in tools.segment_text(output, 1980): await channel.send(tools.wrap_code(out))
    except Exception as e:
        pass # ignoring, most likely exception is "insufficent permissions to write in system channel" which is expected

@DiscordClient.event
async def on_guild_remove(guild):
    local_env = data.GetGuildEnvironment(guild)
    for func in triggers.on_guild_remove: 
        try:
            await func(local_env, guild)
        except Exception as e:
            log.write(e)

################################################################################

################################### STATUS #####################################

async def CheckStatus():
    results = []
    for (name, check) in triggers.Status:
        try:
            results.append( (name, await check()) )
        except Exception as e:
            log.write(e)
    return results

def StatusMessage(results, tim):
    output = f"ZEKE BOT {VERSION} [{REPO_LINK}]\nReport created on: {str(tim)}\n"
    operational = [ (name, val) for (name, val) in results if val == True ]
    failed = [ (name, val) for (name, val) in results if val == False ]
    output = output + "\n"
    for (name, val) in operational: output = output + f"{name}: OK\n"
    if len(failed) > 0:
        output = output + "\n"
        for (name, val) in failed: output = output + f"{name}: FAILED\n"
    else:
        output = output + f"\nALL SYSTEMS OPERATIONAL"
    return output

status_cache = None

async def FetchStatus():
    global status_cache
    if status_cache and (datetime.now() - status_cache[1]).seconds > 60*60: status_cache = None
    if not status_cache: status_cache = (StatusMessage(await CheckStatus(), datetime.now()), datetime.now())
    return status_cache[0]

################################################################################

################################## COMMANDS ####################################

async def cmd_status(ctx, args):
    await ctx.message.add_reaction('????') 
    output = (await FetchStatus()) 
    for out in tools.segment_text(output, 1980): await ctx.message.reply(tools.wrap_code(out), mention_author=False)
    return True
cmd.Add(cmd.parser, "status", cmd_status, "Check status of integration with third party", "")

async def cmd_debug(ctx, args):
    if os.getenv('DEBUG_MODE'):
        await debug.command(ctx, list(args))
    else:
        await ctx.message.reply("Debug tools are disabled server-side. There's nothing you can do about it", mention_author=False)
    return True
cmd.Add(cmd.parser, "debug", cmd_debug, "Tools useful for debugging this bot", "", discord.Permissions.all())

################################################################################

#################################### MAIN ######################################

@DiscordClient.event
async def on_ready():
    each_minute.start()
    print("Initialisation finished")
    print(f'{DiscordClient.user} has connected to Discord!')
    print("Number of servers (guilds) bot is connected to: "+str(len(DiscordClient.guilds)))
    await DiscordClient.change_presence(activity=discord.Game(name=cmd.GetZekeHelpCmd()))

if __name__ == '__main__':
    for func in triggers.OnInitTrigger: 
        try:
            func(DiscordClient)
        except Exception as e:
            log.write(e)
    print("Startup finished. Connecting...")
    DiscordClient.run(os.getenv('DISCORD_TOKEN'))