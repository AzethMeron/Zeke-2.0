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
import main_triggers

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
    await main_triggers.TimerTick(minute, DiscordClient)
    minute = (minute + 1) % 100000

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

@DiscordClient.event
async def on_message(message):
    if message.author.bot:
        return
    # enforce execution of commands
    await DiscordClient.process_commands(message)
    for func in main_triggers.on_message: func(message)
    

@DiscordClient.event
async def on_reaction_add(reaction, user):
    if user.bot:
        return 
    for func in main_triggers.on_reaction_add: func(reaction, user)

@DiscordClient.event        
async def on_reaction_remove(reaction, user):
    if user.bot:
        return 
    for func in main_triggers.on_reaction_remove: func(reaction, user)

################################################################################

@DiscordClient.event
async def on_ready():
    for func in main_triggers.OnInitTrigger: func(DiscordClient)
    each_minute.start()
    print("Initialisation finished")
    print(f'{DiscordClient.user} has connected to Discord!')
    print("Number of servers (guilds) bot is connected to: "+str(len(DiscordClient.guilds)))

if __name__ == '__main__':
    print("Startup finished. Connecting...")
    DiscordClient.run(os.getenv('DISCORD_TOKEN'))