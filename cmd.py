
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
    # Parametried
    if len(args) == 1:
        cmd = args[0]
        if cmd not in parser:
            commands = GetSimilarCommands(parser, cmd, author)
            raise KeyError(f'Command "{cmd}" not found. Did you mean {commands[0]}?')
        if type(parser[cmd]) == type(Parser()):
            return Help(parser[cmd], args[1:], author)
        else:
            return parser[cmd][2]
    # Not parametrized
    output = str()
    for cmd in parser:
        (_, help, _2, perms) = parser[cmd]
        if author.guild_permissions >= perms: output = output + '{0: <10}'.format(cmd) + help + "\n"
    return output

# func(ctx, args)
def Add(parser, cmd, func, help, longhelp, perms = discord.Permissions.none()):
    if cmd in parser:
        raise KeyError(f'{cmd} already present in parser')
    parser[cmd] = (func, help, longhelp, perms)

def GetSimilarCommands(parser, cmd, author):
    commands = [ command for command in parser if author.guild_permissions >= parser[command][3] ]
    commands.append("help")
    commands.sort(key = lambda x: -fuzz.ratio(x, cmd))
    return commands

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
            commands = GetSimilarCommands(parser, cmd, ctx.message.author)
            raise KeyError(f'Command "{cmd}" not found. Did you mean {commands[0]}?')
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