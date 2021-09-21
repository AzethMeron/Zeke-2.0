
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
data.NewGuildEnvAdd("welcome_message", "USER joined the server!") 

################################################################################

async def GetWelcomeChannel(local_env, bot):
    channel_id = local_env["welcome_channel_id"]
    channel = None
    if channel_id:
        channel = bot.get_channel(channel_id)
    return channel

async def GetWelcomeMessage(local_env, member):
    output = local_env["welcome_message"]
    if output:
        output = output.replace("USER", member.name)
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

async def cmd_message(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    if len(args) == 0:
        await ctx.message.reply(local_env["welcome_message"])
        return True
    else:
        local_env["welcome_message"] = ' '.join(args)

parser = cmd.Parser()
cmd.Add(parser, "channel", cmd_channel, "dummy", "dummy")
cmd.Add(parser, "message", cmd_message, "dummy", "dummy")

################################################################################

async def command(ctx, args):
    await cmd.Parse(parser, ctx, args)