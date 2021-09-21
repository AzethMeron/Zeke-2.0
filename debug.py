
import traceback

import tools
import cmd
import data
import triggers

################################################################################

async def cmd_traceback(ctx, args):
    await ctx.message.reply(str(traceback.format_exc()))
    return True

async def cmd_save(ctx, arg):
    data.SaveGuildEnvironment(ctx.message.guild)

################################################################################

parser = cmd.Parser()
cmd.Add(parser, "traceback", cmd_traceback, "dummy", "dummy")
cmd.Add(parser, "save", cmd_save, "dummy", "dummy")

async def command(ctx, args):
    return await cmd.Parse(parser, ctx, args)

################################################################################