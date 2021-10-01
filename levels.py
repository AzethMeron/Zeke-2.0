
import random
import math

import cmd
import triggers
import data
import log
import tools

##########################################################################

data.NewGuildEnvAdd("levels verbose", False)
data.NewUserEnvAdd("level", 0)
data.NewUserEnvAdd("messages", 0)
data.NewUserEnvAdd("experience", 0)
data.NewUserEnvAdd("sent message this minute", False)

##########################################################################

def get_exp():
    return random.randint(10,25)

def exp_to_next_level(level): # formula to be changed?
    return int(70 * (level+1) * math.log(level+2))

##########################################################################

async def level_up(local_env, message, user_env):
    if local_env["levels verbose"]:
        await message.reply(f"Congratulations {message.author.mention}! You've just advanced to {user_env['level']} level.")

async def on_message(local_env, message, normalised_text):
    user_env = data.GetUserEnvironment(local_env, message.author)
    user_env["messages"] += 1
    if not user_env["sent message this minute"]:
        user_env["sent message this minute"] = True
        prev_exp = user_env["experience"]
        next_level_exp = exp_to_next_level(user_env["level"] + 1)
        user_env["experience"] += get_exp()
        if prev_exp < next_level_exp and user_env["experience"] >= next_level_exp:
            user_env["level"] += 1
            await level_up(local_env, message, user_env)

triggers.on_message.append(on_message)

async def each_minute(bot, local_env, guild, minute):
    for member in guild.members:
        user_env = data.GetUserEnvironment(local_env, member)
        if user_env["sent message this minute"]: user_env["sent message this minute"] = False

triggers.Timers.append( (1, each_minute) )

##########################################################################

async def cmd_list(ctx, args):
    guild = ctx.guild
    local_env = data.GetGuildEnvironment(guild)
    ulist = [ (member, data.GetUserEnvironment(local_env, member)["level"], data.GetUserEnvironment(local_env, member)["experience"]) for member in guild.members if data.GetUserEnvironment(local_env, member)["level"] >= 1 ]
    ulist.sort(key = lambda item: -item[1] )
    output = "Level Leaderboard" + "\n"
    for item in ulist:
        output = output + str(item[0].display_name) + " - level " + str(item[1]) + "\n"
    for out in tools.segment_text(output, 1980):
        await ctx.message.reply("```" + out + "```")
    return True

async def cmd_verbose(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.message.author)
    local_env["levels verbose"] = not local_env["levels verbose"]
    await ctx.message.reply(f'Levels verbose: {local_env["levels verbose"]}')
    return True

parser = cmd.Parser()
cmd.Add(parser, "list", cmd_list, "dummy", "dummy")
cmd.Add(parser, "verbose", cmd_verbose, "dummy", "dummy")

async def command(ctx, args):
    return await cmd.Parse(parser, ctx, args)
    