
import cmd
import data
import log
import triggers

##################################################################################################

class ReactionData:
    def __init__(self):
        self.channel_id = None # id
        self.message_id = None # id
        self.reaction_roles = dict() # [emoji] = role_id
    def CheckReactionMessage(self, message):
        if message.channel.id == self.channel_id:
            if message.id == self.message_id:
                return True
        return False
    def GetRoleId(self, emoji):
        if emoji in self.reaction_roles:
            return self.reaction_roles[emoji]
        else:
            return None
    def AddRR(self, emoji, role_id):
        if emoji not in self.reaction_roles:
            self.reaction_roles[emoji] = role_id
        else:
            raise RuntimeWarning(f'Emoji {emoji} is already used')
    def RemoveRR(self, emoji):
        if emoji in self.reaction_roles:
            del self.reaction_roles[emoji]
        else:
            raise RuntimeWarning(f"Emoji {emoji} isn't used")
    def GetList(self):
        return [ (emoji, self.reaction_roles[emoji]) for emoji in self.reaction_roles ]
data.NewGuildEnvAdd("reaction_roles", ReactionData()) # [emoji] = role_id
def GetReactionData(local_env):
    return local_env["reaction_roles"]

##################################################################################################

async def AddReaction(payload, local_env, emoji, member, guild, message):
    reaction_data = GetReactionData(local_env)
    if reaction_data.CheckReactionMessage(message):
        role_id = reaction_data.GetRoleId(str(emoji))
        if role_id:
            role = guild.get_role(role_id)
            await member.add_roles(role)
triggers.raw_reaction_add.append(AddReaction)

async def RemoveReaction(payload, local_env, emoji, member, guild, message):
    reaction_data = GetReactionData(local_env)
    if reaction_data.CheckReactionMessage(message):
        role_id = reaction_data.GetRoleId(str(emoji))
        if role_id:
            role = guild.get_role(role_id)
            await member.remove_roles(role)
triggers.raw_reaction_remove.append(RemoveReaction)

##################################################################################################

async def cmd_set_message(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    reaction_data = GetReactionData(local_env)
    reaction_data.channel_id = ctx.channel.id
    if len(args) > 0:
        reaction_data.message_id = int(args[0])
    elif ctx.message.reference:
        message = ctx.message.reference.resolved
        reaction_data.message_id = message.id
    else:
        reaction_data.message_id = ctx.message.id
    
async def cmd_add_rr(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    if len(args) != 2: raise RuntimeError("Wrong number of arguments")
    reaction_data = GetReactionData(local_env)
    emoji = args[0]
    role_id = ctx.message.raw_role_mentions[0]
    reaction_data.AddRR(emoji, role_id)
    
async def cmd_remove_rr(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    if len(args) != 1: raise RuntimeError("Wrong number of arguments")
    reaction_data = GetReactionData(local_env)
    emoji = args[0]
    reaction_data.RemoveRR(emoji)
    
async def cmd_list_rr(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    reaction_data = GetReactionData(local_env)
    output = "Programmed reaction roles:\n"
    for (emoji, role_id) in reaction_data.GetList(): 
        role = ctx.guild.get_role(role_id)
        output = output + f'{emoji} - {role.mention}\n'
    await ctx.message.reply(output)
    return True

##################################################################################################

parser = cmd.Parser()
cmd.Add(parser, "setup", cmd_set_message, "Set message", "dummy")
cmd.Add(parser, "add", cmd_add_rr, "Add reaction role", "dummy")
cmd.Add(parser, "remove", cmd_remove_rr, "Remove reaction role", "dummy")
cmd.Add(parser, "list", cmd_list_rr, "Show list of programmed reaction roles", "dummy")

async def command(ctx, args):
    return await cmd.Parse(parser, ctx, args)

##################################################################################################