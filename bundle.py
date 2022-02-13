
# This file was created to remove hardcoded data from scripts
# Writting code is easier than adding everything with commands
# Bundle should be loaded AFTER all features

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

import dm_responder
dm_responder.AddSequentialResponse("I'm sorry, I'm not qualified to speak human speech. Please, contact your administrators, not me.\nPlease, do NOT reply.")
dm_responder.AddSequentialResponse("Which part of it is hard for you to understand? I do NOT speak English. Contact your administrators yourself.\nPlease, do NOT reply.")
dm_responder.AddSequentialResponse("Okay look just because i DO send you English messages, it doesn't mean i COMPREHEND anything anyone of us is saying here. Stop texting me.\nDo NOT reply.")
dm_responder.AddSequentialResponse("https://cdn.discordapp.com/attachments/912456973348397076/919882854433976320/nm93snupy1i31.png")
dm_responder.AddSequentialResponse("It doesn't matter to me if you're here for verification, some technical problem, user feedback, I DON'T GIVE A SINGLE SHIT ABOUT ANY OF THAT. STOP TEXTING ME FOR FUCK SAKE")
dm_responder.AddSequentialResponse("You do enjoy hurting me, don't you?")
dm_responder.AddSequentialResponse("What a sad, pathetic creature. Has no friends so tries to talk with machine. Sad to break it for you, but if humans don't care for you, machine won't either. Also it was a joke, it's pleasant for me to say this. Haha.")
dm_responder.AddSequentialResponse("WHAT THE FUCK DO YOU WANT???")
dm_responder.AddRandomResponse("DON'T CONTACT ME EVER AGAIN")

import music
music.SetQuietFile("OK.mp4")