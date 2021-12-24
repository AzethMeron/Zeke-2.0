---
# Zeke-2.0  

Simple discord bot made to learn Discord API.  
Most scripts are library scripts. Callable scripts are called "executable_*"  
executable_main.py - main script of Discord Bot  

NOTE: This bot IS NOT plug&play.  
Features are NOT hardcoded and most things can be changed with use of commands.  
Actually, not only can, but must.   

---
# REQUIREMENTS. Created using programs & libraries:  

Python 3.9  
All python packages required are listed in requirements.txt, install them using pip install -r requirements.txt  
Ffmpeg must be installed and present in PATH environmental variable.  

Tokens must be included in ".env" file in working directory, containing:  
DISCORD_TOKEN="your token here"  
(optional) DETECT_LANGUAGE_TOKEN="your token here"  
(optional) DROPBOX_TOKEN="your token here"  
Discord bot must have "members intent" enabled.  

Dropbox token is optional. If you specify it, all guild data will be saved/loaded from dropbox if local copy isn't available. Useful when there's no persistent memory.   

---
# Disclaimer: UwU translator

uwu_translator.py is extracted from repository of WahidBawa - https://github.com/WahidBawa/UwU-Translator  
All rights on this script goes to WahidBawa, and following license doesn't apply to that script.

---
# Features:  

- Automated translation by using emojis, to any language supported by google translate.
- Music bot features (only youtube)
- Programmable Welcome/Farewell messages.
- Dice rolling.
- Levels (basic but it does work)
- Reaction roles.
- Text generation, summarization with Deep AI.
- Aliases (macros) to shorten frequently used commands.
- Very easily expandable "engine".
- Own command parser.
- Support for multiple servers (guilds, with separate variables & stuff)
- Persistent data stored remotely on Dropbox (optional and easy to reprogram so it works with some other platform)
- (pretty much) Heroku-ready.

More features on the way. Moderation feature TODO  

---
# Commands, how-to-use:  

Zeke comes with own command parser, written in cmd.py.  
Prefix is "zeke". It can be changed by using aliases.  
To read help for any command, put "help" before it.  
For example, "zeke help alias".  

---
# Feature: translation

To translate message, you need react to it (with emoji) corresponding to target language.  
By default there're very few programmed-in languages. You can check the list of them with "zeke translate list"  
To add new language, use "zeke translate add :emoji: :language:", where :language: is two-character long ISO language code.  
There're some joke languages too. You can see the list of them with "zeke translate custom".  

Example - adding japanese translation support:  
zeke translate add :flag_jp: ja  

---
# Feature: reaction roles

Reaction roles is mechanism that grants/removes role from user upon their reaction to specific emoji under specific message.  
To use it, you need to set the message and corelate reactions (emojis) with roles.  
Easiest way to set a message: "zeke rr setup". This will make THIS message a reaction-roles message.  
Then you corelate reactions with roles by using "zeke rr add :emoji: :role:".  
That's it. Everytime user uses reacton , he gets given role. If he removes his reaction, role is removed too.  

Remember to grant bot permission to manage roles, and to place all reaction-roles BELOW bot in permission menager of your server.  
To remove reaction-role, use "zeke rr remove :emoji:"  
To see what reaction-roles are currently used, check "zeke rr list"  

---
# Feature: music from youtube

Most of music commands can only be used when you're in the same voice channel as bot.   
If bot isn't connected to any other channel, it will automatically join.  

There're many commands for music bot, i won't cover them all here. To check help, use "zeke help music".  
To play music, use "zeke music play :arg:". :arg: can be link to youtube video, playlist, or just name of that video.  
To display queue, use "zeke music queue". By default, it displays current song and 5 next in queue.  
To randomize queue, use "zeke music shuffle".  
To vote for skip, use "zeke music vote".  

---
# Feature: Welcome/Farewell messages

Welcome/Farewell messages are sent when user joins/leaves your server.   
They're randomly chosen from programmed list, and sent in channel chosen by you.  
Syntax for both is exactly the same.  

To choose channel for welcome/farewell messages, use "zeke welcome/farewell channel". Channel in which you cast this command will be used.  
To check existing welcome/farewell messages, use "zeke welcome/farewell message list". It will show you list of messages, with indexes.   
To add new message, cast "zeke welcome/farewell message add :your message:".  
To remove message, use "zeke welcome/farewell message remove :id:", where :id: is index taken from list.  

Inside messages, you can refer to arriving/leaving user by USER (this will mention them) or NAME (which will just paste their discord username).  
Example: "zeke welcome message add USER joined the server!"  

---
# Feature: Aliases/macros

You can create aliases (or macros) for any command you need to use. It can also be used to change "prefix" (tho zeke will always work)  
For example, "zeke alias add !play zeke music play" will make "!play" macro for "zeke music play".  
You can also create alias for entire command with arguments. "zeke alias add PlayAMV zeke music play :link to your AMV playlist:"  
"zeke alias add d6 zeke random dice 1 6"  

You can check exisitng aliases with "zeke alias list"  
Alias can be only singular word, and must be first in command. So you CANNOT use "zeke alias add play music play" -> "zeke play ..."  
Also, alias CANNOT refer to another alias.  

---
# Feature: Reactionaries

I'm still think about how this feature should even be named.  
Basically, reactionaries are messages sent automatically after anyone adds to any message specific emoji.  
To get help, use "zeke help react".  

Plain syntax:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;zeke react add :emoji: any text you want  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;zeke react remove :emoji: index  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;zeke react list (optional: :emoji:)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;zeke react random :emoji:  

Most meaningful example: BonkBot. Setup reactionary in the way it sends "bonk go to hornyjail" after usage of :bonk: emoji.  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;zeke react add :bonk: https://cdn.discordapp.com/attachments/912456973348397076/912457896791527484/unknown.png  
Then, after anyone uses :bonk: on message, Zeke will respond with this meme.  
Technically he responds with plain text, but if you use direct link to picture without anythin else, it's converted to just that picture.  
You can also use "zeke react add :bonk: text" multiple times, to add multiple pictures. Then random one will be chosen for every reaction.  

You can combine this feature with alias. By using:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;zeke react random :bonk:  
you can get random reaction from Zeke for :bonk:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;zeke alias add bonk! zeke react random :bonk:  

---
# Engine: The way data is stored, data.py:  

Every guild has its own environment, realised as dictionary. You can get this dict by using data.GetGuildEnvironment(guild). In code it's referred to as "local_env".  
Inside this dictonary, there're additional dictionaries for user data. You can get this by using data.GetUserEnvironment(local_env, user). In code, it's referred to as "user_env".  
All data inside of those must be pickleable, because this is the way data is saved/loaded.  

Additionally, there's temporary environment that can be used with not-pickleable datatypes. This aswell is dictionary. You can get it by using temp.GetTempEnvironment(local_env). In code, it's referred to as "temp_env".  

It's useful to initialise "variables" in enviroments with some data. Here's simple example:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;data.NewGuildEnvAdd("welcome_channel_id", None)  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;data.NewGuildEnvAdd("welcome_message", ["USER joined the server!"])   
Those "variables" will be accessible then in every newcoming guild.  

NO SELFREFERENCING LOOPS INSIDE THIS DATA IS ALLOWED!  
Every time guild data is loaded from disk, it's updated. All new keys from "NewGuildEnvironment()" are copied into guild data.  
This can save you some trouble, but remember it does only work if key wasn't used by that guild before. So if you suddenly change value under the same key, don't expect it to be updated.  
Same applies to temp_env and user_env.  

Note: data declared in temp_env still must be pickleable, but then you can switch it to anything and it will be fine:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;temp.NewTempEnvAdd("music_lock", None)  
Before saving data, engine replaces temp_env of guild with "NewTempEnvironment()", then saves entire local_env and finally swappes tmp_env back to its place. This way, real data stored in temp_env isn't saved but persists after saving.  

---
# Engine: Discord events, triggers.py:  

All discord events are handled by main file, which calls "triggers" stored in lists you can find in triggers.py  
This way, there's no need to modify main just to explicitely call new function. You can just append it to the list.  

---
# Engine: Custom parser, cmd.py: 

To create instance of parser, use  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;parser = cmd.Parser()  
Then you can add commands to that parser with  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;cmd.Add(parser, "command (one word)", function(ctx, args), "optional: short help", "optional: long help", discord.Permissions required)  
You can insert another object of parser instead of function. In this case, longhelp is ignored (it's mostly autogenerated)  

Inside longhelp, you can use word UPLINE to insert full command for which you're writting documentation.   
For example, for "zeke random help dice" -> UPLINE = "zeke random dice"  

Main parser of bot resides in cmd.py, simply named "parser". Refer to it from outside with cmd.parser.  
You can add your own commands/other parsers to it.  

---
# Engine: Adding/removing features: 

Scripts of this bot are segregated into two groups: engine and features.  
Due to how the engine is constructed, you can add features without any changes to engine scripts.  
Read more about "data.py", "triggers.py" and "cmd.py".  
Then all you need to do is to import feature script in executable_main.py.  
To remove any feature, you can just remove that import.  

Limitation: You cannot remove support to feature if both are true  
- it was used previously, and its data is saved in "database".  
- Data of this feature (script) uses class.  

---
# Engine: Environmental variables:

There're more env vars used than I've put in initial requirements.  
Some are mandatory, some are optional, for specific features.  
All apis below have free, limited keys you can get.  

ENGINE ENVIRONMENTAL VARS:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;DISCORD_TOKEN="your discord token - https://discord.com/developers/applications"  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(optional) DETECT_LANGUAGE_TOKEN="your token for detect language - https://detectlanguage.com"  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(optional) DROPBOX_TOKEN="your token for dropbox app - https://www.dropbox.com/developers/documentation/python"  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(optional) DEBUG_MODE="value doesn't matter, but if you set this var then debug tools will be activated and command errors will display full traceback instead of only exception"  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(optional) DATA_SAVE_INTERVAL_MIN=60 # interval between saves of data in minutes, default 60  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(optional) PURGE_DIR_INTERVAL_MIN=360 # interval between purge of temporary directory in minutes, default 360 (6 hours)  
Dropbox token is important cause for systems like Heroku (without permanent memory storage) every restart will result in removal of all data.  

ENVIRONMENTAL VARS OF FEATURES:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(optional) DEEP_AI_KEY="your api key for deep ai - https://deepai.org"  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(optional) SERP_API_KEY="your api key for serp api - https://serpapi.com"  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(optional) MUSIC_PROC_COUNT=4 # number of processes used by music.py to download audio from yt, default 4  

If optional environmental variable isn't set, it uses some default value (that has harsh limitations) or disables given feature.  

