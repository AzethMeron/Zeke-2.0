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
Discord bot must have "members intent" enabled.  

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

More features on the way. Moderation feature TODO  
