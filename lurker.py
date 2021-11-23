
import random
import time
import os

import triggers

CHANCE = int(os.getenv('LURKER_CHANCE')) if os.getenv('LURKER_CHANCE') else 10 # 0 to 100
EMOJI = '👀'
MS = 0 #random.randint(50,100) / 1000

def Success(chance):
    rand = random.randint(1,100)
    return (rand <= chance)

async def OnMessage(local_env, message, normalised_text):
    if Success(CHANCE):
        await message.add_reaction(EMOJI)
        time.sleep(MS)
        await message.remove_reaction(EMOJI, message.guild.me)
triggers.on_message.append(OnMessage)