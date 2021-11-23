
import discord

import cmd
import tools
import triggers
import data
import uwu_translator
import log

################################################################################

import urllib.parse
import requests
import re

api = "https://api.funtranslations.com/translate/"

def fun_translation(lang, text):
    global api
    try:
        text = re.sub(r'\W+', ' ', text)
        url = api + lang + "?" + urllib.parse.urlencode({'text': text})
        response = requests.get(url)
        json = response.json()
        return json['contents']['translated']
    except:
        return "Error, most likely too many requests. Please try in an hour."


################################################################################

default_emojis = dict()
data.NewGuildEnvAdd("reaction_translator", default_emojis) # dict[emoji] = tgt_lang
def GetReactionTranslator(local_env):
    return local_env["reaction_translator"]

custom_lang = dict()

################################################################################

# API for bundle
def AddDefaultTranslation(emoji, langcode):
    default_emojis[emoji] = langcode

# API for bundle
def AddCustomTranslation(name, normalisation_code, func, help):
    custom_lang[name] = (normalisation_code, func, help)

AddCustomTranslation('uwu', 'en', uwu_translator.convert, 'Twanswate text intwo cuwe UwU wanguage :3')
AddCustomTranslation('shakespeare','en', lambda text: fun_translation('shakespeare.json',text), 'helpfile')
AddCustomTranslation('orcish', 'en', lambda text: fun_translation('orcish.json',text), 'helpfile')
AddCustomTranslation('oldenglish', 'en', lambda text: fun_translation('oldenglish.json',text), 'helpfile')
AddCustomTranslation('pirate', 'en', lambda text: fun_translation('pirate.json',text), 'Arr, raise the anchor and translate text into Corsair jargon!')
AddCustomTranslation('yoda', 'en', lambda text: fun_translation('yoda.json',text), 'Text into language of ancient jedi master,  translate.')

################################################################################

async def Reply(message, user, translated_text, src_lang, tgt_lang):
    mess = f"\
    {translated_text}\n\
    {src_lang} -> {tgt_lang}\n\
    Requested by: {user.display_name}"
    await message.reply(mess)

def GetReaction(PartialEmoji, message):
    for reaction in message.reactions:
        if str(PartialEmoji) == str(reaction): return reaction
    return None

async def OnRawReaction(payload, local_env, PartialEmoji, member, guild, message):
    if member.bot: return
    if len(message.content) < 4: return
    reaction = GetReaction(PartialEmoji, message)
    if reaction and reaction.count > 1: return
    emoji = str(PartialEmoji)
    text = message.content
    if emoji in GetReactionTranslator(local_env):
        tgt_lang = GetReactionTranslator(local_env)[emoji]
        (src_lang, _, translated) = ('auto', tgt_lang, text)
        if tgt_lang in custom_lang:
            normalised_lang = custom_lang[tgt_lang][0]
            (src_lang, _, translated) = tools.Translate(normalised_lang, text)
            translated = custom_lang[tgt_lang][1](translated)
        else:
            (src_lang, _, translated) = tools.Translate(tgt_lang, text)
        await message.add_reaction(PartialEmoji)
        await Reply(message, member, translated, src_lang, tgt_lang)
triggers.raw_reaction_add.append(OnRawReaction)

################################################################################

async def cmd_add(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    if len(args) != 2: raise RuntimeError("Incorrect arguments")
    emoji = args.pop(0)
    lang = args.pop(0)
    if emoji in GetReactionTranslator(local_env): raise RuntimeError(f"This emoji is already occupied by '{GetReactionTranslator(local_env)[emoji]}' language")
    GetReactionTranslator(local_env)[emoji] = lang
    
async def cmd_remove(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    emoji = args[0]
    if emoji not in GetReactionTranslator(local_env): raise RuntimeError(f"Emoji {emoji} isn't used by translator")
    del GetReactionTranslator(local_env)[emoji]

async def cmd_list(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    output = "Programmed translations:\n"
    for emoji in GetReactionTranslator(local_env):
        output = output + f'{emoji} -> {GetReactionTranslator(local_env)[emoji]}\n'
    for out in tools.segment_text(output, 1980):
        await ctx.message.reply(out)
    return True

async def cmd_custom(ctx, args):
    output = "Available custom languages:\n"
    for name in custom_lang:
        output = output + f"{name}: {custom_lang[name][2]}\n"
    for out in tools.segment_text(output, 1980): await ctx.message.reply("```"+out+"```")

parser = cmd.Parser()
cmd.Add(parser, "add", cmd_add, "Add emoji translation for language.", "Add emoji translation for language.\nSyntax: zeke translate add <emoji> <language>\n<language> is two-character long ISO language code.")
cmd.Add(parser, "remove", cmd_remove, "Remove emoji translation for language.", "Remove emoji translation for language.\nSyntax: zeke translate remove <emoji>")
cmd.Add(parser, "list", cmd_list, "Display list of current emojis used in translations.", "Display list of current emojis used in translations.\nSyntax: zeke translate list")
cmd.Add(parser, "custom", cmd_custom, "Display list of available custom languages.", "Display list of available custom languages.\nNot real languages obviously.\nSyntax: zeke translate list")

cmd.Add(cmd.parser, "translate", parser, "Setup translation feature", "", discord.Permissions.all())

################################################################################