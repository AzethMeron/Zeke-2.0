
import random
import math
import discord

import cmd
import triggers
import data
import log
import tools

##########################################################################

class LevelData:
    def __init__(self):
        self.level = 0
        self.messages = 0
        self.experience = 0
        self.sent_message = False

data.NewGuildEnvAdd("levels verbose", False)
data.NewUserEnvAdd("LevelData", LevelData())

def GetLevelData(user_env):
    return user_env['LevelData']

##########################################################################

def get_exp():
    return random.randint(10,25)

def exp_to_level(level): # formula to be changed?
    return int(70 * (level+1) * math.log(level+2))

##########################################################################

async def level_up(local_env, message, leveldata):
    if local_env["levels verbose"]:
        await message.reply(f"Congratulations {message.author.mention}! You've just advanced to {leveldata.level} level.", mention_author=False)

async def on_message(local_env, message, normalised_text):
    user_env = data.GetUserEnvironment(local_env, message.author)
    leveldata = GetLevelData(user_env)
    leveldata.messages += 1
    if not leveldata.sent_message:
        leveldata.sent_message = True
        prev_exp = leveldata.experience
        next_leve_threshold = exp_to_level(leveldata.level + 1)
        leveldata.experience += get_exp()
        if leveldata.experience >= next_leve_threshold > prev_exp:
            leveldata.level += 1
            await level_up(local_env, message, leveldata)
triggers.on_message.append(on_message)

async def each_minute(bot, local_env, guild, minute):
    for member in guild.members:
        user_env = data.GetUserEnvironment(local_env, member)
        leveldata = GetLevelData(user_env)
        if leveldata.sent_message: leveldata.sent_message = False
triggers.Timers.append( (1, each_minute) )

##########################################################################

async def cmd_list(ctx, args):
    guild = ctx.guild
    local_env = data.GetGuildEnvironment(guild)
    ulist = []
    for member in guild.members:
        user_env = data.GetUserEnvironment(local_env, member)
        leveldata = GetLevelData(user_env)
        if leveldata.level >= 1:
            ulist.append( (member, leveldata.level, leveldata.experience) )
    ulist.sort(key = lambda item: -item[1] )
    output = "Level Leaderboard" + "\n"
    for item in ulist:
        output = output + str(item[0].display_name) + " - level " + str(item[1]) + "\n"
    for out in tools.segment_text(output, 1980):
        await ctx.message.reply(tools.wrap_code(out), mention_author=False)
    return True

async def cmd_verbose(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.message.guild)
    local_env["levels verbose"] = not local_env["levels verbose"]
    await ctx.message.reply(f'Levels verbose: {local_env["levels verbose"]}', mention_author=False)
    return True

parser = cmd.Parser()
cmd.Add(parser, "list", cmd_list, "Display leaderboard.", "Display leaderboard.")
cmd.Add(parser, "verbose", cmd_verbose, "Toggle verbose levels.", "Toggle whether level up should be announced or not.", discord.Permissions.all())

cmd.Add(cmd.parser, "levels", parser, "Message counter and server levels", "")