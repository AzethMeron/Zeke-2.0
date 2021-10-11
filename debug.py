
import traceback

import tools
import cmd
import data

################################################################################

async def cmd_save(ctx, arg):
    data.SaveGuildEnvironment(ctx.message.guild)

async def cmd_info(ctx, arg):
    output = str(data.GetGuildEnvironment(ctx.message.guild))
    for out in tools.segment_text(output, 1980):
        await ctx.message.reply("```" + out + "```")

################################################################################

parser = cmd.Parser()
cmd.Add(parser, "save", cmd_save, "Enforce save of this server's data", "Enforce save of this server's data.\nNo arguments required.\nSyntax: zeke debug save")
cmd.Add(parser, "info", cmd_info, "Display content of this server's data", "Converts data of this server's data to Python string and displays it here.\nNo arguments required.\nSyntax: zeke debug info")

async def command(ctx, args):
    return await cmd.Parse(parser, ctx, args)

################################################################################