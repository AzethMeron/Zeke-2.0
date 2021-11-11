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

PREFIX = "zeke "
VERSION = "2.0"

load_dotenv() # load environmental variables from file .env
intents = discord.Intents.default()
intents.members = True
DiscordClient = commands.Bot(command_prefix=PREFIX,intents=intents) # create client of discord-bot

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
    
@DiscordClient.event
async def on_command_error(ctx, error):
    await ctx.message.reply(str(error))

################################################################################

############################## DISCORD TRIGGERS ################################

@DiscordClient.event
async def on_message(message):
    if message.author.bot:
        return
    if not message.guild:
        return
    # enforce execution of commands
    await DiscordClient.process_commands(message)
    normalised = tools.EnsureEnglish(message.content)
    local_env = data.GetGuildEnvironment(message.guild)
    for func in triggers.on_message: 
        try:
            await func(local_env, message, normalised)
        except Exception as e:
            log.write(e)

@DiscordClient.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return 
    if not reaction.message.guild:
        return
    local_env = data.GetGuildEnvironment(reaction.message.guild)
    for func in triggers.on_reaction_add: 
        try:
            await func(local_env, reaction, user)
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

@DiscordClient.command(name="music", help="Music bot feature")
async def cmd_music(ctx, *args):
    await music.command(ctx, list(args))

@DiscordClient.command(name="dice", help="Roll dice")
async def cmd_dice(ctx, *args):
    await dice.command(ctx, list(args))

@DiscordClient.command(name="welcome", help="Setup welcome messages")
@has_permissions(administrator=True)
async def cmd_welcome(ctx, *args):
    await welcome.welcome_command(ctx, list(args))

@DiscordClient.command(name="farewell", help="Setup farewell messages")
@has_permissions(administrator=True)
async def cmd_farewell(ctx, *args):
    await welcome.farewell_command(ctx, list(args))

@DiscordClient.command(name="translate", help="Setup translation feature")
@has_permissions(administrator=True)
async def cmd_translate(ctx, *args):
    await translate.command(ctx, list(args))

@DiscordClient.command(name="levels", help="Message counter and server levels")
@has_permissions(administrator=True)
async def cmd_levels(ctx, *args):
    await levels.command(ctx, list(args))

@DiscordClient.command(name="status", help="Check status of integration with third party")
@has_permissions(administrator=True)
async def cmd_status(ctx, *args):
    output = "ZEKE BOT " + VERSION + " [https://github.com/AzethMeron/Zeke-2.0]" + "\n"
    for (name, check) in triggers.Status:
        try:
            output = output + name + ": " + tools.convert_status( (await check()) ) + "\n"
        except Exception as e:
            log.write(e)
    for out in tools.segment_text(output, 1980): await ctx.message.reply("```"+out+"```")

@DiscordClient.command(name="debug", help="Tools useful for debugging this bot")
@has_permissions(administrator=True)
async def cmd_debug(ctx, *args):
    if os.getenv('DEBUG_MODE'):
        await debug.command(ctx, list(args))
    else:
        await ctx.message.reply("Debug tools are disabled server-side. There's nothing you can do about it")

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