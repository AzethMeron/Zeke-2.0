
# This parser should be either rewritten into OOP object
# or just left alone as it is, only updated with fixes
# it's spaghetti code i hate

import os

import traceback
import copy
import tools
import discord
from fuzzywuzzy import fuzz

default_parser = dict()

def Parser():
    return copy.deepcopy(default_parser)

def Help(parser, args, author, prev_args):
    # Parametried
    if len(args) == 1:
        cmd = args[0]
        prev_args.append(cmd)
        if cmd not in parser:
            commands = GetSimilarCommands(parser, cmd, author)
            raise KeyError(f'Command "{cmd}" not found. Did you mean {commands[0]}?')
        if type(parser[cmd][0]) == type(Parser()):
            return parser[cmd][1] + "\n\n" + Help(parser[cmd][0], args[1:], author, prev_args)
        else:
            prev_args.remove('help')
            upline = ' '.join(prev_args)
            return parser[cmd][2].replace('UPLINE', upline)
    # Not parametrized
    output = str()
    for cmd in parser:
        (_, help, _2, perms) = parser[cmd]
        if author.guild_permissions >= perms: output = output + '{0: <10}'.format(cmd) + help + "\n"
    return output

# func(ctx, args)
# you can put func = parser if you're embedding parsers, no need for using lambdas or functions anymore
# If you put func = parser, then longhelp is ignored (help for that parser is called instead)
def Add(parser, cmd, func, help = "dummy", longhelp = "dummy", perms = discord.Permissions.none()):
    if cmd in parser:
        raise KeyError(f'{cmd} already present in parser')
    parser[cmd] = (func, help, longhelp, perms)

def GetSimilarCommands(parser, cmd, author):
    commands = [ command for command in parser if author.guild_permissions >= parser[command][3] ]
    commands.append("help")
    commands.sort(key = lambda x: -fuzz.ratio(x, cmd))
    return commands

async def Parse(parser, ctx, args, prev_args = []):
    try:
        if len(args) == 0: raise KeyError('no command specified. Try "help"')
        cmd = args.pop(0)
        prev_args.append(cmd)
        if cmd == "help":
            help = Help(parser, args, ctx.message.author, prev_args)
            for out in tools.segment_text(help,1980):
                await ctx.message.reply("```"+out+"```")
            return True
        if cmd not in parser:
            commands = GetSimilarCommands(parser, cmd, ctx.message.author)
            raise KeyError(f'Command "{cmd}" not found. Did you mean {commands[0]}?')
        if not ctx.message.author.guild_permissions >= parser[cmd][3]: 
            raise RuntimeError("Insufficent permissions")
        if type(parser[cmd][0]) == type(Parser()):
            feedback = await Parse(parser[cmd][0], ctx, args, prev_args)
        else:
            feedback = await parser[cmd][0](ctx, args)
        if not feedback: await ctx.message.add_reaction('👍')
    except Exception as e:
        if os.getenv('DEBUG_MODE'):
            await ctx.message.reply("Command error: " + str(traceback.format_exc()))
        else:
            await ctx.message.reply("Command error: " + str(e))
    return True