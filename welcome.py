
import traceback
import random


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

################################################################################

async def GetWelcomeChannel(local_env, bot):
    channel_id = local_env["welcome_channel_id"]
    channel = None
    if channel_id:
        try:
            channel = bot.get_channel(channel_id)
        except:
            print(traceback.format_exc())
    return channel

async def GetWelcomeMessage(local_env, member):
    olist = local_env["welcome_message"]
    output = None
    if len(olist) > 0:
        output = random.choice(olist)
    if output:
        output = output.replace("USER", member.mention)
    return output

################################################################################

async def on_member_join(local_env, member):
    channel = await GetWelcomeChannel(local_env, triggers.BOT_REFERENCE)
    if channel:
        output = await GetWelcomeMessage(local_env, member)
        if output:
            await channel.send(output)
triggers.on_member_join.append(on_member_join)

################################################################################

async def cmd_channel(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    local_env["welcome_channel_id"] = ctx.message.channel.id

async def cmd_message_add(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    if len(args) == 0: raise RuntimeError("You forgot to write welcome message dude")
    local_env["welcome_message"].append(' '.join(args))

async def cmd_message_list(ctx, args):
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
    
async def cmd_message_remove(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    index = int(args[0]) - 1
    local_env["welcome_message"].pop(index)

msg_parser = cmd.Parser()
cmd.Add(msg_parser, "add", cmd_message_add, "dummy", "dummy")
cmd.Add(msg_parser, "list", cmd_message_list, "dummy", "dummy")
cmd.Add(msg_parser, "remove", cmd_message_remove, "dummy", "dummy")

async def cmd_message(ctx, args):
    return await cmd.Parse(msg_parser, ctx, args)

parser = cmd.Parser()
cmd.Add(parser, "channel", cmd_channel, "dummy", "dummy")
cmd.Add(parser, "message", cmd_message, "dummy", "dummy")

################################################################################

async def command(ctx, args):
    await cmd.Parse(parser, ctx, args)