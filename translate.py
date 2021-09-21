
import tools
import triggers
import data
import uwu_translator

################################################################################

data.NewGuildEnvAdd("reaction_translator", dict()) # dict[emoji] = tgt_lang
custom_lang = dict()
custom_lang['uwu'] = ('en', uwu_translator.convert)

def GetReactionTranslator(local_env):
    return local_env["reaction_translator"]

################################################################################

def MakeMessage(text, user, src_lang, tgt_lang):
    mess = f"\
    {text}\n\
    {src_lang} -> {tgt_lang}\n\
    Requested by: {user.display_name}"
    return mess

def OnReaction(local_env, reaction, user):
    if reaction.count > 1: 
        return
    emoji = str(reaction.emoji)
    text = reaction.message.content
    if emoji in GetReactionTranslator(local_env):
        tgt_lang = GetReactionTranslator[emoji]
        (src_lang, _, translated) = ('auto', tgt_lang, text)
        if tgt_lang in custom_lang:
            normalised_lang = custom_lang[tgt_lang][0]
            (src_lang, _, translated) = tools.Translate(normalised_lang, text)
            translated = custom_lang[tgt_lang][1](translated)
        else:
            (src_lang, _, translated) = tools.Translate(tgt_lang, text)
        await reaction.message.add_reaction(reaction.emoji)
        await reaction.message.reply(MakeMessage(translated, user, src_lang, tgt_lang))
    
triggers.on_reaction_add.append(OnReaction)

################################################################################