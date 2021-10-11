
import os

import traceback
import copy
import tools

default_parser = dict()

def Parser():
    return copy.deepcopy(default_parser)

def Help(parser, args):
    output = str()
    if len(args) == 1:
        cmd = args[0]
        if cmd not in parser:
            raise KeyError(f'{cmd} - command not found')
        output = output + parser[cmd][2]
        return output
    for cmd in parser:
        (_, help, _2) = parser[cmd]
        output = output + f'{cmd}           ' + help + "\n"
    return output

# func(ctx, args)
def Add(parser, cmd, func, help, longhelp):
    if cmd in parser:
        raise KeyError(f'{cmd} already present in parser')
    parser[cmd] = (func, help, longhelp)

async def Parse(parser, ctx, args):
    try:
        if len(args) == 0: raise KeyError("no command specified")
        cmd = args.pop(0)
        if cmd == "help":
            help = Help(parser, args)
            for out in tools.segment_text(help,1980):
                await ctx.message.reply("```"+out+"```")
            return True
        if cmd not in parser:
            raise KeyError(f'{cmd} - command not found')
        if not await parser[cmd][0](ctx, args):
            await ctx.message.add_reaction('👍')
    except Exception as e:
        if os.getenv('DEBUG_MODE'):
            await ctx.message.reply("Command error: " + str(traceback.format_exc()))
        else:
            await ctx.message.reply("Command error: " + str(e))
    return True