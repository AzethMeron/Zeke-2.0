
# This parser should be either rewritten into OOP object
# or just left alone as it is, only updated with fixes
# it's spaghetti code i hate

# HOW TO USE
# parser = cmd.Parser()
# cmd.Add(parser, "command (one word)", function(ctx, args), "optional: short help", "optional: long help", discord.Permissions required)
# You can insert another object of parser instead of function. Note that then longholp is ignored
# Inside longhelp, you can use word UPLINE to insert full command for which you're writting documentation
# for example, for "zeke random help dice" -> UPLINE = "zeke random dice"

import os
import traceback
import copy
import discord
from fuzzywuzzy import fuzz

import tools
import triggers
import data

########################################################################################################################

PREFIX = "zeke"
default_parser = dict()

def Parser():
    return copy.deepcopy(default_parser)

default_aliases = dict()
data.NewGuildEnvAdd('alias', default_aliases)

########################################################################################################################

def GetZekeHelpCmd():
    return PREFIX + " " + "help"

########################################################################################################################

# MAIN PARSER OF ENGINE
parser = Parser()

########################################################################################################################

def Help(parser, args, author, prev_args):
    # Parametried
    if len(args) == 1:
        cmd = args[0]
        prev_args.append(cmd)
        if cmd not in parser:
            commands = GetSimilarCommands(parser, cmd, author)
            raise KeyError(f'Command "{cmd}" not found. Did you mean "{commands[0]}"?')
        if type(parser[cmd][0]) == type(Parser()):
            return parser[cmd][1] + "\n\n" + Help(parser[cmd][0], args[1:], author, prev_args)
        else:
            prev_args.remove('help')
            upline = ' '.join(prev_args)
            return parser[cmd][2].replace('UPLINE', upline)
    # Not parametrized
    output = str()
    for cmd in parser:
        (_, help, _2, perms) = parser[cmd]
        if author.guild_permissions >= perms: output = output + '{0: <10}'.format(cmd) + help + "\n"
    return output

def GetSimilarCommands(parser, cmd, author):
    commands = [ command for command in parser if author.guild_permissions >= parser[command][3] ]
    commands.append("help")
    commands.sort(key = lambda x: -fuzz.ratio(x, cmd))
    return commands

########################################################################################################################

async def ProcessCommands(local_env, message, DiscordClient):
    content = message.content.split()
    if len(content) >= 1:
        if content[0] == PREFIX: # command
            ctx = await DiscordClient.get_context(message)
            await Parse(parser, ctx, content[1:], content[:1])
            return True
        elif content[0] in local_env['alias']: # alias
            new_content = message.content.replace(content[0], local_env['alias'][content[0]])
            message.content = new_content
            return await ProcessCommands(local_env, message, DiscordClient)
    return False

########################################################################################################################

# func(ctx, args)
# you can put func = parser if you're embedding parsers, no need for using lambdas or functions anymore
# If you put func = parser, then longhelp is ignored (help for that parser is called instead)
def Add(parser, cmd, func, help = "dummy", longhelp = "dummy", perms = discord.Permissions.none()):
    if cmd in parser:
        raise KeyError(f'{cmd} already present in parser')
    parser[cmd] = (func, help, longhelp, perms)

async def Parse(parser, ctx, args, prev_args = []):
    try:
        if len(args) == 0: raise KeyError('no command specified. Try "help"')
        cmd = args.pop(0)
        prev_args.append(cmd)
        if cmd == "help":
            help = Help(parser, args, ctx.message.author, prev_args)
            for out in tools.segment_text(help,1980):
                await ctx.message.reply(tools.wrap_code(out), mention_author=False)
            return True
        if cmd not in parser:
            commands = GetSimilarCommands(parser, cmd, ctx.message.author)
            raise KeyError(f'Command "{cmd}" not found. Did you mean "{commands[0]}"?')
        if not ctx.message.author.guild_permissions >= parser[cmd][3]: 
            raise RuntimeError("Insufficent permissions")
        if type(parser[cmd][0]) == type(Parser()):
            feedback = await Parse(parser[cmd][0], ctx, args, prev_args)
        else:
            feedback = await parser[cmd][0](ctx, args)
        if not feedback: await ctx.message.add_reaction('👍')
    except Exception as e:
        if os.getenv('DEBUG_MODE'):
            await ctx.message.reply("Command error: " + str(traceback.format_exc()), mention_author=False)
        else:
            await ctx.message.reply("Command error: " + str(e), mention_author=False)
    return True

# API for bundle
def AddDefaultAlias(alias, cmd):
    if alias in default_aliases: raise RuntimeError(f"Alias {alias} already exists")
    default_aliases[alias] = cmd

########################################################################################################################

def AddAlias(local_env, alias, cmd):
    tmp = cmd.split()
    if len(tmp) >= 1 and tmp[0] in local_env['alias']: raise RuntimeError("Alias cannot refer to another alias")
    local_env['alias'][alias] = cmd

def RemoveAlias(local_env, alias):
    if alias in local_env['alias']:
        del local_env['alias'][alias]
    else:
        raise RuntimeError(f"There's no {alias} alias")

def AliasList(local_env):
    return [ (alias, local_env['alias'][alias]) for alias in local_env['alias'] ]

async def cmd_alias_add(ctx, args):
    if len(args) < 2: raise RuntimeError("Not enough arguments")
    local_env = data.GetGuildEnvironment(ctx.guild)
    alias = args[0]
    command = ' '.join(args[1:])
    AddAlias(local_env, alias, command)

async def cmd_alias_remove(ctx, args):
    if len(args) < 1: raise RuntimeError("Not enough arguments")
    local_env = data.GetGuildEnvironment(ctx.guild)
    alias = args[0]
    RemoveAlias(local_env, alias)

async def cmd_alias_list(ctx, args):
    local_env = data.GetGuildEnvironment(ctx.guild)
    output = "Created aliases:\n"
    for (alias, command) in AliasList(local_env):
        output = output + f'{alias} -> {command}\n'
    for out in tools.segment_text(output, 1980): await ctx.message.reply(tools.wrap_code(out), mention_author=False)
    return True

alias_parser = Parser()
Add(alias_parser, "add", cmd_alias_add, "Create alias.", "Create alias (macro) for command.\nThis can be used to replace prefix, or as fast way to use common command.\n\nSyntac:\nUPLINE <alias> <command> - now you can type in <alias> to run <command.\nExample: UPLINE !play zeke music play - now you can play music by using !play", discord.Permissions.all())
Add(alias_parser, "remove", cmd_alias_remove, "Remove existing alias.", "Remove alias.\n\nSyntax: UPLINE <alias>",discord.Permissions.all())
Add(alias_parser, "list", cmd_alias_list, "Display existing macros", "Display existing macros\n\nUPLINE")
Add(parser, "alias", alias_parser, "Manage aliases (macros) for commands", "")

########################################################################################################################