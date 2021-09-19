
import traceback

def Parser():
    return dict()

# func return (bool, err_message)
def Add(parser, key, func):
    if key in parser:
        raise KeyError(f'{key} already present in parser')
    parser[key] = func

async def Parse(parser, ctx, args):
    try:
        key = args.pop(0)
        if key not in parser:
            raise KeyError(f'{key} - command not found')
        results = await parser[key](ctx,args)
        if results[0]:
            await ctx.message.add_reaction('👍')
        else:
            await ctx.message.reply("Command failed: " + str(results[1]))
    except Exception as e:
        await ctx.message.reply("Command error: " + str(e) + str(traceback.format_exc()))