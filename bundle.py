
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