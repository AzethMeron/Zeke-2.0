
OnInitTrigger = [] # func(bot)
on_message = [] # func(message)
on_reaction_add = [] # func(reaction, user)
on_reaction_remove = [] # func(reaction, user)

# ( minutes, func(bot, local_env, guild, minute) )
# minutes < 100000
Timers = []
def TimerAdd(minutes, func):
    Timers.append( (minutes, func) )   
async def TimerTick(minute, DiscordClient):
    for (m,func) in Timers:            
        if abs(minute) % m == 0:
            for guild in DiscordClient.guilds:
                local_env = data.GetGuildEnvironment(guild)
                await func(DiscordClient, local_env, guild, minute)