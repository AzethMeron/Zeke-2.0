
# ( minutes, func(bot, local_env, guild, minute) )
# minutes < 100000
Timers = []

def Add(minutes, func):
    Timers.append( (minutes, func) )
    
async def Tick(minute, DiscordClient):
    for (m,func) in Timers:            
        if abs(minute) % m == 0:
            for guild in DiscordClient.guilds:
                local_env = data.GetGuildEnvironment(guild)
                await func(DiscordClient, local_env, guild, minute)