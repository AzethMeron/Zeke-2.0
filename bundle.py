
# This file was created to removed hardcoded data from scripts
# Writting code is easier than adding everything with commands
# Bundle shoudl be loaded AFTER all features

import translate

translate.AddDefaultTranslation('🇵🇱', 'pl')
translate.AddDefaultTranslation('🇬🇧', 'en')
translate.AddDefaultTranslation('🇪🇦', 'es')
translate.AddDefaultTranslation('🇷🇺', 'ru')
translate.AddDefaultTranslation('🇫🇷', 'fr')
translate.AddDefaultTranslation('🇮🇹', 'it')

import welcome

welcome.AddDefaultWelcome("USER joined the server!")
welcome.AddDefaultFarewell("NAME left the server :C")

import cmd

cmd.AddDefaultAlias("alexa", "zeke music")
cmd.AddDefaultAlias("!play", "zeke music play")
cmd.AddDefaultAlias("!skip", "zeke music skip")
cmd.AddDefaultAlias("!fs", "zeke music fs")
cmd.AddDefaultAlias("!shuffle", "zeke music shuffle")
cmd.AddDefaultAlias("!queue", "zeke music queue")
cmd.AddDefaultAlias("!loop", "zeke music loop")
cmd.AddDefaultAlias("!insert", "zeke music insert")
cmd.AddDefaultAlias("!remove", "zeke music remove")

cmd.AddDefaultAlias("!roll", "zeke random roll")
cmd.AddDefaultAlias("!word", "zeke random word")
