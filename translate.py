
import cmd
import tools
import triggers
import data
import uwu_translator
import traceback

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

async def OnReaction(local_env, reaction, user):
    try:
        if reaction.message.author.bot:
            return None
        if reaction.count > 1: 
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
    except:
        print(traceback.format_exc())
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
    pass

async def cmd_list(ctx, args):
    pass

parser = cmd.Parser()
cmd.Add(parser, "add", cmd_add, "dummy", "dummy")
cmd.Add(parser, "remove", cmd_remove, "dummy", "dummy")
cmd.Add(parser, "list", cmd_list, "dummy", "dummy")

async def command(ctx, args):
    return await cmd.Parse(parser, ctx, args)
    
################################################################################