#!/usr/bin/env python

import os
import discord # Discord API
from discord.ext import tasks
from discord.ext import commands
from dotenv import load_dotenv # ENV vars
from discord.ext.commands import has_permissions, MissingPermissions, CommandNotFound

# TOOLS
import file
import temp
import data
import timers
import cmd

# FEATURES
import music

PREFIX = "alexa"
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
    await timers.Tick(minute, DiscordClient)
    minute = (minute + 1) % 100000

################################################################################

#################################### INIT ######################################

def OnInitTrigger(bot):
    return None

################################################################################

@DiscordClient.event
async def on_ready():
    OnInitTrigger(DiscordClient)
    each_minute.start()
    print("Initialisation finished")
    print(f'{DiscordClient.user} has connected to Discord!')
    print("Number of servers (guilds) bot is connected to: "+str(len(DiscordClient.guilds)))


if __name__ == '__main__':
    print("Startup finished. Connecting...")
    DiscordClient.run(os.getenv('DISCORD_TOKEN'))