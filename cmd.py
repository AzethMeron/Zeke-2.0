
import os

import traceback
import copy
import tools
import discord
from fuzzywuzzy import fuzz

default_parser = dict()

def Parser():
    return copy.deepcopy(default_parser)

def Help(parser, args, author):
    output = str()
    if len(args) == 1:
        cmd = args[0]
        if cmd not in parser:
            raise KeyError(f'{cmd} - command not found')
        output = output + parser[cmd][2]
        return output
    for cmd in parser:
        (_, help, _2, perms) = parser[cmd]
        if author.guild_permissions >= perms: output = output + '{0: <10}'.format(cmd) + help + "\n"
    return output

# func(ctx, args)
def Add(parser, cmd, func, help, longhelp, perms = discord.Permissions.none()):
    if cmd in parser:
        raise KeyError(f'{cmd} already present in parser')
    parser[cmd] = (func, help, longhelp, perms)

async def Parse(parser, ctx, args):
    try:
        if len(args) == 0: raise KeyError('no command specified. Try "help"')
        cmd = args.pop(0)
        if cmd == "help":
            help = Help(parser, args, ctx.message.author)
            for out in tools.segment_text(help,1980):
                await ctx.message.reply("```"+out+"```")
            return True
        if cmd not in parser:
            commands = [ command for command in parser if ctx.message.author.guild_permissions >= parser[command][3] ]
            commands.append("help")
            commands.sort(key = lambda x: -fuzz.ratio(x, cmd))
            raise KeyError(f'Command "{cmd}" not found. Did you mean {commands[0]}?')
            return True
        if not ctx.message.author.guild_permissions >= parser[cmd][3]: 
            raise RuntimeError("Insufficent permissions")
        if not await parser[cmd][0](ctx, args):
            await ctx.message.add_reaction('👍')
    except Exception as e:
        if os.getenv('DEBUG_MODE'):
            await ctx.message.reply("Command error: " + str(traceback.format_exc()))
        else:
            await ctx.message.reply("Command error: " + str(e))
    return True