
import traceback
import copy

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
        return "```" + output + "```"
    for cmd in parser:
        (_, help, _2) = parser[cmd]
        output = output + f'{cmd}           ' + help + "\n"
    return "```" + output + "```"

# func(ctx, args)
def Add(parser, cmd, func, help, longhelp):
    if cmd in parser:
        raise KeyError(f'{cmd} already present in parser')
    parser[cmd] = (func, help, longhelp)

async def Parse(parser, ctx, args):
    try:
        cmd = args.pop(0)
        if cmd == "help":
            await ctx.message.reply(Help(parser, args))
            return True
        if cmd not in parser:
            raise KeyError(f'{cmd} - command not found')
        if not await parser[cmd][0](ctx, args):
            await ctx.message.add_reaction('👍')
    except Exception as e:
        await ctx.message.reply("Command error: " + str(traceback.format_exc())) # temporary
    return True