
import traceback

import tools
import cmd
import data

################################################################################

async def cmd_traceback(ctx, args):
    await ctx.message.reply(str(traceback.format_exc()))
    return True

async def cmd_save(ctx, arg):
    data.SaveGuildEnvironment(ctx.message.guild)

async def cmd_info(ctx, arg):
    output = str(data.GetGuildEnvironment(ctx.message.guild))
    for out in tools.segment_text(output, 1980):
        await ctx.message.reply("```" + out + "```")

################################################################################

parser = cmd.Parser()
cmd.Add(parser, "traceback", cmd_traceback, "dummy", "dummy")
cmd.Add(parser, "save", cmd_save, "dummy", "dummy")
cmd.Add(parser, "info", cmd_info, "dummy", "dummy")

async def command(ctx, args):
    return await cmd.Parse(parser, ctx, args)

################################################################################