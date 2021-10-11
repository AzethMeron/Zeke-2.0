
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
    return True

parser = cmd.Parser()
cmd.Add(parser, "roll", cmd_roll, "Roll a dice.", "Roll a dice.\nUsage:\n- zeke dice roll - get random number from 1 to 6\n- zeke dice roll <max> - get random number from 1 to <max>\n- zeke dice roll <min> <max> - get random number from <min> to <max>")

async def command(ctx, args):
    return await cmd.Parse(parser, ctx, args)
    
