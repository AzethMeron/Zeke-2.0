
# Discord Events
on_message = [] # async func(local_env, message, normalised_text)
on_reaction_add = [] # async func(local_env, reaction, user)
on_reaction_remove = [] # async func(local_env, reaction, user)
on_member_join = [] # async func(local_env, member)
on_member_remove = [] # async func(local_env, member)
raw_reaction_add = [] # async (payload, local_env, emoji, member, guild, message)
raw_reaction_remove = [] # async (payload, local_env, emoji, member, guild, message)

# Data
PreSaveTrigger = [] # func(local_env): # Called BEFORE saving
PostSaveTrigger = [] # func(local_env): # Called AFTER saving
PostLoadTrigger = [] # func(local_env): # Called AFTER loading

# Temp
PostTempPurge = [] # func(local_env)

# Check status of feature (integration)
Status = [] # (name, async func()), func must return True/False

# Reference to Bot
# i hate this global variable but i hate passing it everywhere as argument even more
BOT_REFERENCE = None # Note: it is initiated AFTER establishing connection. Before that, it is None

def GetBot():
    if BOT_REFERENCE:
        return BOT_REFERENCE
    else:
        raise RuntimeError("Bot referenced via triggers before reference was initiated")

# Main triggers
OnInitTrigger = [] # func(bot), called BEFORE connecting to discord
# ( minutes, async func(bot, local_env, guild, minute) )
# 0 <= minutes < 100000
Timers = []
import cmd
parser = cmd.Parser()