
# Main triggers
OnInitTrigger = [] # func(bot)

# Discord Events
on_message = [] # func(local_env, message)
on_reaction_add = [] # func(local_env, reaction, user)
on_reaction_remove = [] # func(local_env, reaction, user)

# Data
PreSaveTrigger = [] # func(local_env): # Called BEFORE saving
PostSaveTrigger = [] # func(local_env): # Called AFTER saving
PostLoadTrigger = [] # func(local_env): # Called AFTER loading

# ( minutes, func(bot, local_env, guild, minute) )
# minutes < 100000
Timers = []