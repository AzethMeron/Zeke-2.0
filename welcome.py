
import random

import log
import tools
import file
import temp
import data
import triggers
import cmd

# Clausule
uses = triggers.BOT_REFERENCE

################################################################################

data.NewGuildEnvAdd("welcome_channel_id", None)
data.NewGuildEnvAdd("welcome_message", ["USER joined the server!"]) 
data.NewGuildEnvAdd("farewell_channel_id", None)
data.NewGuildEnvAdd("farewell_message", ["NAME left the server :C"]) 

################################################################################

def GetChannel(channel_id, bot):
    channel = None
    if channel_id:
        try:
            channel = bot.get_channel(channel_id)
        except Exception as e:
            log.write(e)
    return channel

def GetMessage(olist, member):
    output = None
    if len(olist) > 0:
        output = random.choice(olist)
    if output:
        output = output.replace("USER", member.mention)
        output = output.replace("NAME", member.name)
    return output

async def GetWelcomeChannel(local_env, bot):
    channel_id = local_env["welcome_channel_id"]
    return GetChannel(channel_id, bot)

async def GetFarewellChannel(local_env, bot):
    channel_id = local_env["farewell_channel_id"]
    return GetChannel(channel_id, bot)

async def GetWelcomeMessage(local_env, member):
    olist = local_env["welcome_message"]
    return GetMessage(olist, member)

async def GetFarewellMessage(local_env, member):
    olist = local_env["farewell_message"]
    return GetMessage(olist, member)

################################################################################

async def on_member_join(local_env, member):
    channel = await GetWelcomeChannel(local_env, triggers.BOT_REFERENCE)
    if channel:
        output = await GetWelcomeMessage(local_env, member)
        if output:
            await channel.send(output)
triggers.on_member_join.append(on_member_join)

async def on_member_remove(local_env, member):
    channel = await GetFarewellChannel(local_env, triggers.BOT_REFERENCE)
    if channel:
        output = await GetFarewellMessage(local_env, member)
        if output:
            await channel.send(output)
triggers.on_member_remove.append(on_member_remove)

################################################################################

async def cmd_welcome_channel(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    local_env["welcome_channel_id"] = ctx.message.channel.id

async def cmd_welcome_message_add(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    if len(args) == 0: raise RuntimeError("You forgot to write welcome message dude")
    local_env["welcome_message"].append(' '.join(args))

async def cmd_welcome_message_list(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    olist = local_env["welcome_message"]
    num_min = 0
    num_max = min(len(olist), 10)
    if len(args) == 1:
        num_max = min(len(olist), int(args[0]))
    if len(args) == 2:
        num_min = max(0, int(args[0])-1)
        num_max = min(len(olist), int(args[1]))
        if num_min > num_max: raise RuntimeError("Very funny")
    output = "Programmed welcome messages:\n"
    for i in range(num_min, num_max):
        output = output + f'{i+1}. {olist[i]}\n'
    for out in tools.segment_text(output, 1980):
        await ctx.message.reply("```" + out + "```")
    return True
    
async def cmd_welcome_message_remove(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    index = int(args[0]) - 1
    local_env["welcome_message"].pop(index)

msg_parser_welcome = cmd.Parser()
cmd.Add(msg_parser_welcome, "add", cmd_welcome_message_add, "dummy", "dummy")
cmd.Add(msg_parser_welcome, "list", cmd_welcome_message_list, "dummy", "dummy")
cmd.Add(msg_parser_welcome, "remove", cmd_welcome_message_remove, "dummy", "dummy")

async def cmd_welcome_message(ctx, args):
    return await cmd.Parse(msg_parser_welcome, ctx, args)

parser_welcome = cmd.Parser()
cmd.Add(parser_welcome, "channel", cmd_welcome_channel, "dummy", "dummy")
cmd.Add(parser_welcome, "message", cmd_welcome_message, "dummy", "dummy")

################################################################################

async def welcome_command(ctx, args):
    await cmd.Parse(parser_welcome, ctx, args)
    
################################################################################

async def cmd_farewell_channel(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    local_env["farewell_channel_id"] = ctx.message.channel.id

async def cmd_farewell_message_add(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    if len(args) == 0: raise RuntimeError("You forgot to write farewell message dude")
    local_env["farewell_message"].append(' '.join(args))

async def cmd_farewell_message_list(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    olist = local_env["farewell_message"]
    num_min = 0
    num_max = min(len(olist), 10)
    if len(args) == 1:
        num_max = min(len(olist), int(args[0]))
    if len(args) == 2:
        num_min = max(0, int(args[0])-1)
        num_max = min(len(olist), int(args[1]))
        if num_min > num_max: raise RuntimeError("Very funny")
    output = "Programmed farewell messages:\n"
    for i in range(num_min, num_max):
        output = output + f'{i+1}. {olist[i]}\n'
    for out in tools.segment_text(output, 1980):
        await ctx.message.reply("```" + out + "```")
    return True
    
async def cmd_farewell_message_remove(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    index = int(args[0]) - 1
    local_env["farewell_message"].pop(index)

msg_parser_farewell = cmd.Parser()
cmd.Add(msg_parser_farewell, "add", cmd_farewell_message_add, "dummy", "dummy")
cmd.Add(msg_parser_farewell, "list", cmd_farewell_message_list, "dummy", "dummy")
cmd.Add(msg_parser_farewell, "remove", cmd_farewell_message_remove, "dummy", "dummy")

async def cmd_farewell_message(ctx, args):
    return await cmd.Parse(msg_parser_farewell, ctx, args)

parser_farewell = cmd.Parser()
cmd.Add(parser_farewell, "channel", cmd_farewell_channel, "dummy", "dummy")
cmd.Add(parser_farewell, "message", cmd_farewell_message, "dummy", "dummy")

async def farewell_command(ctx, args):
    await cmd.Parse(parser_farewell, ctx, args)

################################################################################