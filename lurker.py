
import random
import time
import os
import discord

import triggers
import data
import cmd

################################################################################

lurker_data = dict()
lurker_data['emoji'] = '👀'
lurker_data['min_chance'] = 1
lurker_data['max_chance'] = 10
data.NewGuildEnvAdd('lurker_data', lurker_data)

def GetLurkerData(local_env):
    return local_env['lurker_data']

################################################################################

def Success(chance):
    rand = random.randint(1,100)
    return (rand <= chance)

async def OnMessage(local_env, message, normalised_text):
    lurker = GetLurkerData(local_env)
    min_chance = lurker['min_chance']
    max_chance = lurker['max_chance']
    emoji = lurker['emoji']
    chance = random.randint(min_chance, max_chance)
    if Success(chance):
        await message.add_reaction(emoji)
        await message.remove_reaction(emoji, message.guild.me)
triggers.on_message.append(OnMessage)

################################################################################

async def cmd_chance(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    lurker = GetLurkerData(local_env)
    if len(args) != 2: raise RuntimeError("Incorrect number of arguments (min_chance max_chance expected)")
    min_chance = int(args[0])
    max_chance = int(args[1])
    if min_chance < 0 or min_chance > 100: raise RuntimeError("Minimal chance must be within (0,100)")
    if max_chance < min_chance or max_chance > 100: raise RuntimeError("Maximal chance must be within (min_chance, 100)")
    lurker['min_chance'] = min_chance
    lurker['max_chance'] = max_chance

async def cmd_emoji(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    lurker = GetLurkerData(local_env)
    if len(args) != 1: raise RuntimeError("Incorrect number of arguments (emoji expected)")
    emoji = args[0]
    try:
        await ctx.message.add_reaction(emoji)
        await ctx.message.remove_reaction(emoji, ctx.guild.me)
    except Exception as e:
        raise RuntimeError(f"Cannot add emoji {emoji}")
    lurker['emoji'] = emoji

async def cmd_settings(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    lurker = GetLurkerData(local_env)
    output = "Lurker settings:\n" + f"Minimal chance: {lurker['min_chance']}\n" + f"Maximal chance: {lurker['max_chance']}\n" + f"Emoji: {lurker['emoji']}\n"
    await ctx.message.reply(output)
    return True

################################################################################

parser = cmd.Parser()
cmd.Add(parser, "chance", cmd_chance, "", "", discord.Permissions.all())
cmd.Add(parser, "emoji", cmd_emoji, "", "", discord.Permissions.all())
cmd.Add(parser, "settings", cmd_settings, "", "")

cmd.Add(cmd.parser, "lurker", parser, "Setup lurker", "")

################################################################################