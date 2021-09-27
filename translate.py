
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
        return "Too many requests, please try again later :C"


################################################################################

default_emojis = dict()
default_emojis['🇵🇱'] = 'pl'
default_emojis['🇬🇧'] = 'en'
default_emojis['🇪🇦'] = 'es'
default_emojis['🇷🇺'] = 'ru'
default_emojis['🇫🇷'] = 'fr'
default_emojis['🇮🇹'] = 'it'

data.NewGuildEnvAdd("reaction_translator", default_emojis) # dict[emoji] = tgt_lang
custom_lang = dict()
custom_lang['uwu'] = ('en', uwu_translator.convert, 'Twanswate text intwo cuwe UwU wanguage :3')
custom_lang['shakespeare'] = ('en', lambda text: fun_translation('shakespeare.json',text), 'helpfile')
custom_lang['orcish'] = ('en', lambda text: fun_translation('orcish.json',text), 'helpfile')
custom_lang['oldenglish'] = ('en', lambda text: fun_translation('oldenglish.json',text), 'helpfile')
custom_lang['pirate'] = ('en', lambda text: fun_translation('pirate.json',text), 'helpfile')
custom_lang['yoda'] = ('en', lambda text: fun_translation('yoda.json',text), 'helpfile')
custom_lang['wow'] = ('en', lambda text: fun_translation('wow.json',text), 'helpfile')
custom_lang['draconic'] = ('en', lambda text: fun_translation('draconic.json',text), 'helpfile')
custom_lang['gungan'] = ('en', lambda text: fun_translation('gungan.json',text), 'helpfile')

def GetReactionTranslator(local_env):
    return local_env["reaction_translator"]

################################################################################

def MakeMessage(text, user, src_lang, tgt_lang):
    mess = f"\
    {text}\n\
    {src_lang} -> {tgt_lang}\n\
    Requested by: {user.display_name}"
    return mess

async def OnReaction(local_env, reaction, user):
    try:
        if reaction.message.author.bot:
            return None
        if reaction.count > 1: 
            return None
        if len(reaction.message.content) < 4:
            return None
        emoji = str(reaction.emoji)
        text = reaction.message.content
        if emoji in GetReactionTranslator(local_env):
            tgt_lang = GetReactionTranslator(local_env)[emoji]
            (src_lang, _, translated) = ('auto', tgt_lang, text)
            if tgt_lang in custom_lang:
                normalised_lang = custom_lang[tgt_lang][0]
                (src_lang, _, translated) = tools.Translate(normalised_lang, text)
                translated = custom_lang[tgt_lang][1](translated)
            else:
                (src_lang, _, translated) = tools.Translate(tgt_lang, text)
            await reaction.message.add_reaction(reaction.emoji)
            await reaction.message.reply(MakeMessage(translated, user, src_lang, tgt_lang))
    except Exception as e:
        log.write(e)
triggers.on_reaction_add.append(OnReaction)

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
cmd.Add(parser, "add", cmd_add, "dummy", "dummy")
cmd.Add(parser, "remove", cmd_remove, "dummy", "dummy")
cmd.Add(parser, "list", cmd_list, "dummy", "dummy")
cmd.Add(parser, "custom", cmd_custom, "dummy", "dummy")

async def command(ctx, args):
    return await cmd.Parse(parser, ctx, args)
    
################################################################################