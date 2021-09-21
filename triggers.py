
# Main triggers
OnInitTrigger = [] # func(bot), called BEFORE connecting to discord
# ( minutes, async func(bot, local_env, guild, minute) )
# 0 <= minutes < 100000
Timers = []

# Discord Events
on_message = [] # async func(local_env, message)
on_reaction_add = [] # async func(local_env, reaction, user)
on_reaction_remove = [] # async func(local_env, reaction, user)
on_member_join = [] # async func(local_env, member)

# Data
PreSaveTrigger = [] # func(local_env): # Called BEFORE saving
PostSaveTrigger = [] # func(local_env): # Called AFTER saving
PostLoadTrigger = [] # func(local_env): # Called AFTER loading

# Temp
PostTempPurge = [] # func(local_env)

# Reference to Bot
# i hate this global variable but i hate passing it everywhere as argument even more
BOT_REFERENCE = None