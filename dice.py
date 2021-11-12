
import random

import cmd
import tools

async def cmd_roll(ctx, args):
    min_val = 1
    max_val = 6
    times = 1
    if len(args) == 1:
        max_val = int(args[0])
    elif len(args) == 2:
        min_val = min(int(args[0]), int(args[1]))
        max_val = max(int(args[0]), int(args[1]))
    elif len(args) == 3:
        min_val = min(int(args[0]), int(args[1]))
        max_val = max(int(args[0]), int(args[1]))
        times = int(args[2])
    output = "Dice rolled: "
    total = 0
    for i in range(0, times):
        roll = random.randint(min_val, max_val)
        output = output + f'{roll} '
        total = total + roll
    if times > 1: output = output + "\n" + f'Sum: {total}' + "\n" + f"Average: {total/times}"
    for out in tools.segment_text(output, 1980): await ctx.message.reply("```" + out + "```")
    return True

async def cmd_sequence(ctx, args):
    min_val = 1
    max_val = 10
    step = 1
    if len(args) == 1:
        max_val = int(args[0])
    elif len(args) == 2:
        min_val = min(int(args[0]), int(args[1]))
        max_val = max(int(args[0]), int(args[1]))
    elif len(args) == 3:
        min_val = min(int(args[0]), int(args[1]))
        max_val = max(int(args[0]), int(args[1]))
        step = int(args[2])
    sequence = [ i for i in range(min_val, max_val+1, step) ]
    random.shuffle(sequence)
    output = "Sequence:"
    for i in sequence: output = output + f' {i}'
    for out in tools.segment_text(output, 1980): await ctx.message.reply("```" + out + "```")

parser = cmd.Parser()
cmd.Add(parser, "roll", cmd_roll, "Roll a dice.", "Roll a dice.\nUsage:\n- zeke dice roll - get random number from 1 to 6\n- zeke dice roll <max> - get random number from 1 to <max>\n- zeke dice roll <min> <max> - get random number from <min> to <max>")
cmd.Add(parser, "sequence", cmd_sequence, "Generate sequence of numbers, randomly shuffled.", "TODO")

async def command(ctx, args):
    return await cmd.Parse(parser, ctx, args)
    
