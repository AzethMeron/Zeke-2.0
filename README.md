---
# Zeke-2.0  

Simple discord bot made to learn Discord API.  
Most scripts are library scripts. Callable scripts are called "executable_*"  
executable_main.py - main script of Discord Bot  

---
# REQUIREMENTS. Created using programs & libraries:  

Python 3.9  
All python packages required are listed in requirements.txt, install them using pip install -r requirements.txt  
Ffmpeg must be installed and present in PATH environmental variable.  

Tokens must be included in ".env" file in working directory, containing:  
DISCORD_TOKEN="your token here"  
DETECT_LANGUAGE_TOKEN="your token here"  
(optional) DROPBOX_TOKEN="your token here"  
Discord bot must have "members intent" enabled.  

Dropbox token is optional. If you specify it, all guild data will be saved/loaded from dropbox if local copy isn't available. Useful when there's no persistent memory.   

---
# Disclaimer: UwU translator

uwu_translator.py is extracted from repository of WahidBawa - https://github.com/WahidBawa/UwU-Translator  
All rights on this script goes to WahidBawa, and following license doesn't apply to that script.

---
# License 
Copyright (c) 2021 Jakub Grzana (https://github.com/AzethMeron) 

All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission. 

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

---
# Features:  

- Automated translation by using emojis, to any language supported by google translate.
- Music bot features (only youtube)
- Programmable Welcome/Farewell messages.
- Dice rolling.
- Levels (basic but it does work)
- Very easily expandable "engine"
- Own command parser (perhaps discord.py one is better but... ANYWAY)
- Support for multiple servers (guilds, with separate variables & stuff)
- Persistent data stored remotely on Dropbox (optional and easy to reprogram so it works with some other platform)
- (pretty much) Heroku-ready

More features on the way. Moderation feature TODO  

---
# Commands, how-to-use:  

Zeke comes with own command parser, but also uses Discord cmd parser for first layer. So it's inconsistent and cumbersome. Sorry about that.  

To get first layer of help, use:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;zeke help  
To get help about particular commands, use:  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;zeke :cmd: help  
Sometimes command have subcommands. Their help can be reached by using  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;zeke :cmd: help :subcmd:  

---
# The way data is stored:  

Every guild has its own environment, realised as dictionary. You can get this dict by using data.GetGuildEnvironment(guild). In code it's referred to as "local_env".  
Inside this dictonary, there're additional dictionaries for user data. You can get this by using data.GetUserEnvironment(local_env, user). In code, it's referred to as "user_env".  
All data inside of those must be pickleable, because this is the way data is saved/loaded.  

Additionally, there's temporary environment that can be used with not-pickleable datatypes. This aswell is dictionary. You can get it by using temp.GetTempEnvironment(local_env). In code, it's referred to as "temp_env".  

It's useful to initialise "variables" in enviroments with some data. Here's simple example:  
data.NewGuildEnvAdd("welcome_channel_id", None)  
data.NewGuildEnvAdd("welcome_message", ["USER joined the server!"])   
Those "variables" will be accessible then in every newcoming guild.  

NO SELFREFERENCING LOOPS INSIDE THIS DATA IS ALLOWED!  
Every time guild data is loaded from disk, it's updated. All new keys from "NewGuildEnvironment()" are copied into guild data.  
This can save you some trouble, but remember it does only work if key wasn't used by that guild before. So if you suddenly change value under the same key, don't expect it to be updated.  
Same applies to temp_env and user_env.  

Note: data declared in temp_env still must be pickleable, but then you can switch it to anything and it will be fine:  
temp.NewTempEnvAdd("music_lock", None)  
Before saving data, engine replaces temp_env of guild with "NewTempEnvironment()", then saves entire local_env and finally swappes tmp_env back to its place. This way, real data stored in temp_env isn't saved but persists after saving.  

---
# Triggers:  

All discord events are handled by main file, which calls "triggers" stored in lists you can find in triggers.py  
This way, there's no need to modify main just to explicitely call new function. You can just append it to the list.  
