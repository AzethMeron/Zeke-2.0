#!/usr/bin/env python

import os
import discord # Discord API
from discord.ext import tasks
from discord.ext import commands
from dotenv import load_dotenv # ENV vars
from discord.ext.commands import has_permissions, MissingPermissions, CommandNotFound
import traceback

# TOOLS
import file
import temp
import data
import cmd
import triggers

# FEATURES
import music

PREFIX = "alexa "
load_dotenv() # load environmental variables from file .env
intents = discord.Intents.default()
DiscordClient = commands.Bot(command_prefix=PREFIX,intents=intents) # create client of discord-bot

#################################### TIMER #####################################

minute = 1
@tasks.loop(minutes=1)
async def each_minute():
    global minute
    # purge temporary dir, once per day
    if abs(minute) % 1440 == 0:
        print("Purging temporary directory")
        temp.PurgeTempDir()
    await TimerTick(minute, DiscordClient)
    minute = (minute + 1) % 100000

async def TimerTick(minute, DiscordClient):
    for (m,func) in triggers.Timers:            
        if abs(minute) % m == 0:
            for guild in DiscordClient.guilds:
                local_env = data.GetGuildEnvironment(guild)
                await func(DiscordClient, local_env, guild, minute)

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
    # enforce execution of commands
    await DiscordClient.process_commands(message)
    local_env = data.GetGuildEnvironment(message.guild)
    for func in triggers.on_message: func(local_env, message)

@DiscordClient.event
async def on_raw_reaction_add(reaction, user):
    if user.bot:
        return 
    local_env = data.GetGuildEnvironment(reaction.message.guild)
    for func in triggers.on_reaction_add: func(local_env, reaction, user)

@DiscordClient.event        
async def on_raw_reaction_remove(reaction, user):
    if user.bot:
        return
    local_env = data.GetGuildEnvironment(reaction.message.guild)
    for func in triggers.on_reaction_remove: func(local_env, reaction, user)

################################################################################

################################## COMMANDS ####################################

@DiscordClient.command(name="music", help="Dummy")
#@has_permissions(administrator=True)
async def cmd_music(ctx, *args):
    await music.command(ctx, list(args))

################################################################################

#################################### MAIN ######################################

@DiscordClient.event
async def on_ready():
    each_minute.start()
    print("Initialisation finished")
    print(f'{DiscordClient.user} has connected to Discord!')
    print("Number of servers (guilds) bot is connected to: "+str(len(DiscordClient.guilds)))

if __name__ == '__main__':
    for func in triggers.OnInitTrigger: func(DiscordClient)
    print("Startup finished. Connecting...")
    DiscordClient.run(os.getenv('DISCORD_TOKEN'))