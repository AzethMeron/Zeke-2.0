
import random
import discord

import log
import tools
import file
import temp
import data
import triggers
import cmd

################################################################################

default_welcome_list = []
default_farewell_list = []

data.NewGuildEnvAdd("welcome_channel_id", None)
data.NewGuildEnvAdd("welcome_message", default_welcome_list) 
data.NewGuildEnvAdd("farewell_channel_id", None)
data.NewGuildEnvAdd("farewell_message", default_farewell_list) 

################################################################################

# API for bundle
def AddDefaultWelcome(text):
    default_welcome_list.append(text)
def AddDefaultFarewell(text):
    default_farewell_list.append(text)

################################################################################

def GetChannel(channel_id, guild):
    channel = None
    if channel_id:
        try:
            channel = guild.get_channel(channel_id)
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

async def GetWelcomeChannel(local_env, guild):
    channel_id = local_env["welcome_channel_id"]
    return GetChannel(channel_id, guild)

async def GetFarewellChannel(local_env, guild):
    channel_id = local_env["farewell_channel_id"]
    return GetChannel(channel_id, guild)

async def GetWelcomeMessage(local_env, member):
    olist = local_env["welcome_message"]
    return GetMessage(olist, member)

async def GetFarewellMessage(local_env, member):
    olist = local_env["farewell_message"]
    return GetMessage(olist, member)

################################################################################

async def on_member_join(local_env, member):
    channel = await GetWelcomeChannel(local_env, member.guild)
    if channel:
        output = await GetWelcomeMessage(local_env, member)
        if output:
            await channel.send(output)
triggers.on_member_join.append(on_member_join)

async def on_member_remove(local_env, member):
    channel = await GetFarewellChannel(local_env, member.guild)
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
    (num_min, num_max) = tools.list_size_args(args, olist, 0, 10)
    output = "Programmed welcome messages:\n"
    for i in range(num_min, num_max):
        output = output + f'{i+1}. {olist[i]}\n'
    for out in tools.segment_text(output, 1980):
        await ctx.message.reply(tools.wrap_code(out), mention_author=False)
    return True
    
async def cmd_welcome_message_remove(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    index = int(args[0]) - 1
    local_env["welcome_message"].pop(index)

msg_parser_welcome = cmd.Parser()
cmd.Add(msg_parser_welcome, "add", cmd_welcome_message_add, "Add welcome message.", "Add welcome message to the list.\nSyntax: zeke welcome message add <text>\nYou can use USER to mention arriving user, and NAME to put his username in text.")
cmd.Add(msg_parser_welcome, "list", cmd_welcome_message_list, "Display list of programmed welcome messages.", "Display list of programmed welcome messages.\nSyntax: zeke welcome message list")
cmd.Add(msg_parser_welcome, "remove", cmd_welcome_message_remove, "Remove welcome message from list.", "Remove welcome message from list.\nSyntax: zeke welcome message remove <index>")

parser_welcome = cmd.Parser()
cmd.Add(parser_welcome, "channel", cmd_welcome_channel, "Set channel into which welcome messages will be sent", "Set channel into which welcome messages will be sent\nSyntax: zeke welcome channel")
cmd.Add(parser_welcome, "message", msg_parser_welcome, "Commands related to welcome messages itself.", "Commands related to welcome messages itself.\nThis bot allows you to create multiple welcome messages, of which one will be randomly chosen.\nSyntax: zeke welcome messages <cmd>")
    
cmd.Add(cmd.parser, "welcome", parser_welcome, "Setup welcome messages", "", discord.Permissions.all())

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
    (num_min, num_max) = tools.list_size_args(args, olist, 0, 10)
    output = "Programmed farewell messages:\n"
    for i in range(num_min, num_max):
        output = output + f'{i+1}. {olist[i]}\n'
    for out in tools.segment_text(output, 1980):
        await ctx.message.reply(tools.wrap_code(out), mention_author=False)
    return True
    
async def cmd_farewell_message_remove(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    index = int(args[0]) - 1
    local_env["farewell_message"].pop(index)

msg_parser_farewell = cmd.Parser()
cmd.Add(msg_parser_farewell, "add", cmd_farewell_message_add, "Add farewell message.", "Add farewell message to the list.\nSyntax: zeke farewell message add <text>\nYou can use NAME to put his username in text")
cmd.Add(msg_parser_farewell, "list", cmd_farewell_message_list, "Display list of programmed farewell messages.", "Display list of programmed farewell messages.\nSyntax: zeke farewell message list")
cmd.Add(msg_parser_farewell, "remove", cmd_farewell_message_remove, "Remove farewell message from list.", "Remove farewell message from list.\nSyntax: zeke farewell message remove <index>")

parser_farewell = cmd.Parser()
cmd.Add(parser_farewell, "channel", cmd_farewell_channel, "Set channel into which farewell messages will be sent", "Set channel into which farewell messages will be sent\nSyntax: zeke farewell channel")
cmd.Add(parser_farewell, "message", msg_parser_farewell, "Commands related to farewell messages itself.", "Commands related to farewell messages itself.\nThis bot allows you to create multiple farewell messages, of which one will be randomly chosen.\nSyntax: zeke farewell messages <cmd>")

cmd.Add(cmd.parser, "farewell", parser_farewell, "Setup farewell messages", "", discord.Permissions.all())

################################################################################