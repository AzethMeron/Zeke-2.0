
import discord
import random

import tools
import cmd
import data
import log
import triggers

##################################################################################################

# Reactionaries - my idea for bot responding with text for specific reactions/commands
# This can be used for easy "reactionary memes". You need to use only straight link to image as "text"
# You can also make alias to "zeke react random :emoji:" so you can give reaction by responding with some funny word ("bonk!"

# zeke react add :emoji: :text:
# zeke react remove :emoji: :index:
# zeke react list (optional :emoji:)
# zeke react random :emoji:

##################################################################################################

default_reactions = dict()
data.NewGuildEnvAdd("reactionary", default_reactions) # [emoji] = [texts]

def GetReactionaryData(local_env):
    return local_env["reactionary"]

##################################################################################################

# API for bundle
def AddDefaultReact(emoji, text):
    if emoji not in default_reactions: default_reactions[emoji] = []
    default_reactions[emoji].append(text)

##################################################################################################

def GetReaction(PartialEmoji, message):
    for reaction in message.reactions:
        if str(PartialEmoji) == str(reaction): return reaction
    return None

async def AddReaction(payload, local_env, PartialEmoji, member, guild, message):
    reaction = GetReaction(PartialEmoji, message)
    if reaction and reaction.count > 1: return
    ######################################
    emoji = str(PartialEmoji)
    reactionary = GetReactionaryData(local_env)
    ######################################
    if emoji in reactionary:
        output = random.choice(reactionary[emoji])
        await message.reply(output, mention_author=False)
        await message.add_reaction(PartialEmoji)
triggers.raw_reaction_add.append(AddReaction)

##################################################################################################

async def cmd_add(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    if len(args) < 2: raise RuntimeError("Not enough arguments")
    reactionary = GetReactionaryData(local_env)
    emoji = args[0]
    text = ' '.join(args[1:])
    if emoji not in reactionary: reactionary[emoji] = []
    reactionary[emoji].append(text)

async def cmd_remove(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    if len(args) < 1: raise RuntimeError("Not enough arguments")
    reactionary = GetReactionaryData(local_env)
    emoji = args[0]
    if not emoji in reactionary: raise RuntimeError(f"Unused emoji {emoji}")
    if len(args) == 1:
        del reactionary[emoji]
    elif len(args) == 2:
        index = int(args[1])
        if not (index >=1 and index <= len(reactionary[emoji])): raise RuntimeError(f"Wrong index {index}")
        reactionary[emoji].pop(index-1)
        if len(reactionary[emoji]) == 0: del reactionary[emoji]
    else:
        raise RuntimeError("Wrong number of arguments")
    
async def cmd_list(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    reactionary = GetReactionaryData(local_env)
    if len(args) == 1:
        emoji = args[0]
        if not emoji in reactionary: raise RuntimeError(f"Unused emoji {emoji}")
        output = f"Reactionary posts for {emoji}" + "\n"
        for i in range(0, len(reactionary[emoji])):
            text = reactionary[emoji][i]
            output = output + f"{i+1}. {text}\n"
        for out in tools.segment_text(output, 1980): await ctx.message.reply(tools.wrap_code(out), mention_author=False)
    else:
        output = "List of emojis used for reactionary memes:"
        for emoji in reactionary:
            output = output + ' ' + emoji
        await ctx.message.reply(output, mention_author=False)
    return True
    
async def cmd_random(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    if len(args) < 1: raise RuntimeError("Not enough arguments")
    reactionary = GetReactionaryData(local_env)
    emoji = args[0]
    if not emoji in reactionary: raise RuntimeError(f"Unused emoji {emoji}")
    output = random.choice(reactionary[emoji])
    message = ctx.message
    if message.reference: message = message.reference.resolved
    await message.reply(output, mention_author=False)
    return True

async def cmd_change_emoji(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    if len(args) < 2: raise RuntimeError("Not enough arguments")
    reactionary = GetReactionaryData(local_env)
    emoji1 = args[0] # src
    emoji2 = args[1] # tgt
    if not emoji1 in reactionary: raise RuntimeError(f"Unused emoji {emoji1}")
    reactionary[emoji2] = reactionary[emoji1]
    del reactionary[emoji1]

##################################################################################################

parser = cmd.Parser()
cmd.Add(parser, "add", cmd_add, "Add reactionary", "", discord.Permissions.all())
cmd.Add(parser, "remove", cmd_remove, "Remove reactionary", "", discord.Permissions.all())
cmd.Add(parser, "list", cmd_list, "Get list of reactionaries", "")
cmd.Add(parser, "random", cmd_random, "Get random reaction", "")
cmd.Add(parser, "change", cmd_change_emoji, "Change emoji", "", discord.Permissions.all())

cmd.Add(cmd.parser, "react", parser, "Add reactionaries", "")

##################################################################################################