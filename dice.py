
import random

import cmd

async def cmd_roll(ctx, args):
    val = 0
    if len(args) == 0:
        val = random.randint(1,6)
    elif len(args) == 1:
        val = random.randint(1,int(args[0]))
    elif len(args) == 2:
        val = random.randint(int(args[0]), int(args[1]))
    else:
        raise RuntimeError("Too many arguments")
    await ctx.message.reply("Dice rolled: " + str(val))

parser = cmd.Parser()
cmd.Add(parser, "roll", cmd_roll, "dummy", "dummy")

async def command(ctx, args):
    return await cmd.Parse(parser, ctx, args)
    
