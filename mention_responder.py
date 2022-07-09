
# Another shitposting feature
# Bot reacts with some message every time person is mentioned

import random

import data
import triggers
import cmd
import tools

##################################################################################################

data.NewUserEnvAdd("MentionResponse", [100, []] )
def GetResponseData(user_env): 
    return user_env["MentionResponse"]
    
##################################################################################################

async def OnMessage(local_env, message, normalised_text):
    for member in message.mentions:
        if message.reference:
            mes = message.reference.resolved
            if mes and mes.author.id == member.id: continue
        user_env = data.GetUserEnvironment(local_env, member)
        [chance, responses] = GetResponseData(user_env)
        if len(responses) > 0:
            response = random.choice(responses)
            if tools.Success(chance):
                try:
                    await message.reply(response, mention_author=False)
                except:
                    pass
triggers.on_message.append(OnMessage)

##################################################################################################

async def cmd_add(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    user_env = data.GetUserEnvironment(local_env, ctx.author)
    [chance, responses] = GetResponseData(user_env)
    text = ' '.join(args)
    responses.append(text)

async def cmd_list(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    user_env = data.GetUserEnvironment(local_env, ctx.author)
    [chance, responses] = GetResponseData(user_env)
    output = f"User {ctx.author.name}\nChance per mention: {chance}\n"
    for id, response in enumerate(responses):
        output = output + f"{id+1} {response}\n"
    for out in tools.segment_text(output, 1980): await ctx.message.reply(tools.wrap_code(out), mention_author=False)
    return True

async def cmd_remove(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    user_env = data.GetUserEnvironment(local_env, ctx.author)
    [chance, responses] = GetResponseData(user_env)
    id = int(args[0]) - 1
    if id < 0 or id > len(responses): raise RuntimeError(f"Invalid index {id+1}")
    responses.pop(id)

async def cmd_chance(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    user_env = data.GetUserEnvironment(local_env, ctx.author)
    d = GetResponseData(user_env)
    val = int(args[0])
    d[0] = min(max(val,0), 100)

##################################################################################################

parser = cmd.Parser()

cmd.Add(parser, "add", cmd_add, "Add message to be used when you're mentioned.", "Add message to be used when you're mentioned.\nUPLINE message")
cmd.Add(parser, "list", cmd_list, "See list of random messages that can be used upon being mentioned.", "See list of random messages that can be used upon being mentioned.\nNo arguments required.")
cmd.Add(parser, "chance", cmd_chance, "Set chance for response upon being mentioned", "Set chance for response upon being mentioned (in %), 100 by default.")
cmd.Add(parser, "remove", cmd_remove, "Remove message (by index)", "Remove message by index.\nUPLINE index\nYou can get index by checking your list of messages.")

cmd.Add(cmd.parser, "menres", parser, "Automatic responses to you being mentioned", "")

##################################################################################################