
import tools
import file
import copy
import triggers

# by Jakub Grzana
guilddir = ".database"
guild_envs = dict()
# im terribly sorry for ambiguous names

#####################################################################################################

NewUser = dict()
NewGuild = dict()

def NewUserEnvAdd(key, data):
    if key in NewUser:
        raise KeyError(f'{key} already present in New User Env')
    NewUser[key] = data

def NewGuildEnvAdd(key, data):
    if key in NewGuild:
        raise KeyError(f'{key} already present in New Guild Env') 
    NewGuild[key] = data

#####################################################################################################

def NewUserEnvironment():
    return copy.deepcopy(NewUser)

def NewGuildEnvironment():
    return copy.deepcopy(NewGuild)
    
def RecursiveDictUpdate(dict_data, dict_temp):
    for key in dict_temp:
        if type(dict_temp[key]) == type(dict()):
            if key not in dict_data:
                dict_data[key] = dict()
            RecursiveDictUpdate(dict_data[key], dict_temp[key])
        else:
            if key not in dict_data:
                dict_data[key] = dict_temp[key]

#####################################################################################################

def LoadGuildEnvironment(guild):
    file.EnsureDir(guilddir)
    filepath = guilddir + "/" + tools.Hash(guild.id) + ".bse"
    if not file.Exist(filepath):
        guild_envs[guild.id] = NewGuildEnvironment()
    else:
        guild_envs[guild.id] = file.Load(filepath)
        RecursiveDictUpdate(guild_envs[guild.id], NewGuildEnvironment())
    for func in triggers.PostLoadTrigger: func(guild_envs[guild.id])
        
def SaveGuildEnvironment(guild):
    file.EnsureDir(guilddir)
    filepath = guilddir + "/" + tools.Hash(guild.id) + ".bse"
    local_env = GetGuildEnvironment(guild)
    for func in triggers.PreSaveTrigger: func(local_env)
    file.Save(filepath,local_env)
    for func in triggers.PostSaveTrigger: func(local_env)

#####################################################################################################

def GetGuildEnvironment(guild):
    if guild.id in guild_envs:
        return guild_envs[guild.id]
    else:
        LoadGuildEnvironment(guild)
        return guild_envs[guild.id]

def GetUserEnvironment(local_env, user):
    if tools.Hash(user.id) in local_env['users']:
        user_env = local_env['users'][tools.Hash(user.id)]
        RecursiveDictUpdate(user_env, NewUserEnvironment())
        return user_env
    else:
        local_env['users'][tools.Hash(user.id)] = NewUserEnvironment()
        return local_env['users'][tools.Hash(user.id)]

def GuildInfo(guild):
    local_env = GetGuildEnvironment(guild)
    info = "**Informations about guild**: " + guild.name + "\n"
    for key in local_env:
        if key == 'users':
            continue
        info = info + key + " = " + str(local_env[key]) + "\n"
    return info