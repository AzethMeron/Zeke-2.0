
import traceback
import copy

default_parser = dict()

def Parser():
    return copy.deepcopy(default_parser)

def Help(parser):
    output = str()
    for cmd in parser:
        (_, help) = parser[cmd]
        output = output + f'{cmd}   ' + help + "\n"
    return "```" + output + "```"

# func(ctx, args)
def Add(parser, cmd, func, help):
    if cmd in parser:
        raise KeyError(f'{cmd} already present in parser')
    parser[cmd] = (func, help)

async def Parse(parser, ctx, args):
    try:
        cmd = args.pop(0)
        if cmd == "help":
            await ctx.message.reply(Help(parser))
            return None
        if cmd not in parser:
            raise KeyError(f'{cmd} - command not found')
        try:
            await parser[cmd][0](ctx, args)
            await ctx.message.add_reaction('👍')
        except Exception as e:
            await ctx.message.reply("Command failed: " + str(e))
    except Exception as e:
        await ctx.message.reply("Command error: " + str(e))