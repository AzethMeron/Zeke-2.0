#!/usr/bin/env python

import os
import discord # Discord API
from discord.ext import tasks
from discord.ext import commands
from dotenv import load_dotenv # ENV vars
from discord.ext.commands import has_permissions, MissingPermissions, CommandNotFound
import traceback

# TOOLS
import tools
import file
import temp
import data
import cmd
import triggers
import debug

# FEATURES
import music
import welcome

PREFIX = "zeke "
load_dotenv() # load environmental variables from file .env
intents = discord.Intents.default()
intents.members = True
DiscordClient = commands.Bot(command_prefix=PREFIX,intents=intents) # create client of discord-bot

#################################### TIMER #####################################

minute = 1
@tasks.loop(minutes=1)
async def each_minute():
    global minute
    if minute % (6*60) == 0:
        temp.PurgeTempDir(DiscordClient)
    if minute % (60) == 0:
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
                except:
                    print(traceback.format_exc())

################################################################################

################################### ERROR ######################################

@DiscordClient.event
async def on_error(event, *args, **kwargs):
    print("UNHANDLED EXCEPTION")
    print(event)
    print(traceback.format_exc())
    
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
    (_1, _2, normalised) = tools.Translate('en', message.content)
    local_env = data.GetGuildEnvironment(message.guild)
    for func in triggers.on_message: await func(local_env, message, normalised)

@DiscordClient.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return 
    if not reaction.message.guild:
        return
    local_env = data.GetGuildEnvironment(reaction.message.guild)
    for func in triggers.on_reaction_add: await func(local_env, reaction, user)

@DiscordClient.event        
async def on_reaction_remove(reaction, user):
    if user.bot:
        return
    if not reaction.message.guild:
        return
    local_env = data.GetGuildEnvironment(reaction.message.guild)
    for func in triggers.on_reaction_remove: await func(local_env, reaction, user)

@DiscordClient.event
async def on_member_join(member):
    local_env = data.GetGuildEnvironment(member.guild)
    for func in triggers.on_member_join: await func(local_env, member)

################################################################################

################################## COMMANDS ####################################

@DiscordClient.command(name="music", help="Dummy")
async def cmd_music(ctx, *args):
    await music.command(ctx, list(args))

@DiscordClient.command(name="welcome", help="Dummy")
@has_permissions(administrator=True)
async def cmd_music(ctx, *args):
    await welcome.command(ctx, list(args))

@DiscordClient.command(name="debug", help="Dummy")
@has_permissions(administrator=True)
async def cmd_debug(ctx, *args):
    await debug.command(ctx, list(args))

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
    for func in triggers.OnInitTrigger: func(DiscordClient)
    print("Startup finished. Connecting...")
    DiscordClient.run(os.getenv('DISCORD_TOKEN'))