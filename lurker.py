
import random
import time
import os

import triggers

################################################################################

EMOJI = '👀'

################################################################################

def Success(chance):
    rand = random.randint(1,100)
    return (rand <= chance)

async def OnMessage(local_env, message, normalised_text):
    chance = random.randint(8,25)
    if Success(chance):
        await message.add_reaction(EMOJI)
        await message.remove_reaction(EMOJI, message.guild.me)
triggers.on_message.append(OnMessage)

################################################################################