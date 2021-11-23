
import random
import dice
from random_word import RandomWords
R = RandomWords()

import cmd
import tools

async def cmd_dice(ctx, args):
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
    return True

async def cmd_word(ctx, args):
    num = 1
    if len(args) >= 1:
        num = int(args[0])
    words = R.get_random_words(limit=num)
    output = "Random words for you: " + ', '.join(words)
    for out in tools.segment_text(output, 1980): await ctx.message.reply("```" + out + "```")
    return True

async def cmd_roll(ctx, args):
    if len(args) == 0: raise RuntimeError("You forgot about arguments m8?")
    command = ''.join(args)
    result = dice.roll(command)
    int(result)
    await ctx.message.reply(f"{command} = {result}\n")
    return True

parser = cmd.Parser()
cmd.Add(parser, "roll", cmd_roll, "Roll a dice", "TODO")
cmd.Add(parser, "number", cmd_dice, "Get random number.", "Get random number.\nUsage:\n- UPLINE - get random number from 1 to 6\n- UPLINE <max> - get random number from 1 to <max>\n- UPLINE <min> <max> - get random number from <min> to <max>\n- UPLINE <min> <max> <times> - generate many random numbers in one go, calculate sum and average")
cmd.Add(parser, "sequence", cmd_sequence, "Generate sequence of numbers, randomly shuffled.", "TODO")
cmd.Add(parser, "word", cmd_word, "TODO", "TODO")
    
cmd.Add(cmd.parser, "random", parser, "Get random values/words", "")