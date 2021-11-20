#!/usr/bin/env python

import os
import discord # Discord API
from discord.ext import tasks
from discord.ext import commands
from dotenv import load_dotenv # ENV vars
from discord.ext.commands import has_permissions, MissingPermissions, CommandNotFound

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
import dice
import mode
import levels
import text_ai
import reaction_roles

load_dotenv() # load environmental variables from file .env
intents = discord.Intents.default()
intents.members = True
DiscordClient = commands.Bot(command_prefix="unused",intents=intents) # create client of discord-bot
VERSION = "2.0"

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
    if not message.guild: return
    normalised = tools.EnsureEnglish(message.content)
    local_env = data.GetGuildEnvironment(message.guild)
    await cmd.ProcessCommands(local_env, message, DiscordClient)
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
async def on_reaction_remove(reaction, user):
    if user.bot:
        return
    if not reaction.message.guild:
        return
    local_env = data.GetGuildEnvironment(reaction.message.guild)
    for func in triggers.on_reaction_remove: 
        try:
            await func(local_env, reaction, user)
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

################################################################################

################################## COMMANDS ####################################

async def cmd_status(ctx, args):
    await ctx.message.add_reaction('👍') 
    output = "ZEKE BOT " + VERSION + " [https://github.com/AzethMeron/Zeke-2.0]" + "\n"
    for (name, check) in triggers.Status:
        try:
            output = output + name + ": " + tools.convert_status( (await check()) ) + "\n"
        except Exception as e:
            log.write(e)
    for out in tools.segment_text(output, 1980): await ctx.message.reply("```"+out+"```")
    return True
cmd.Add(cmd.parser, "status", cmd_status, "Check status of integration with third party", "", discord.Permissions.all())

async def cmd_debug(ctx, args):
    if os.getenv('DEBUG_MODE'):
        await debug.command(ctx, list(args))
    else:
        await ctx.message.reply("Debug tools are disabled server-side. There's nothing you can do about it")
    return True
cmd.Add(cmd.parser, "debug", cmd_debug, "Tools useful for debugging this bot", "", discord.Permissions.all())

################################################################################

#################################### MAIN ######################################

@DiscordClient.event
async def on_ready():
    triggers.BOT_REFERENCE = DiscordClient
    each_minute.start()
    print("Initialisation finished")
    print(f'{DiscordClient.user} has connected to Discord!')
    print("Number of servers (guilds) bot is connected to: "+str(len(DiscordClient.guilds)))

if __name__ == '__main__':
    try:
        for func in triggers.OnInitTrigger: func(DiscordClient)
    except Exception as e:
        log.write(e)
    print("Startup finished. Connecting...")
    DiscordClient.run(os.getenv('DISCORD_TOKEN'))