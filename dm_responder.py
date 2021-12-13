
import triggers
import random 

# REASON WHY THIS EXIST
# i will add welcome/farewell messages with DMs
# there's incredibly high probability ppl will reply to bot
# so autoresponder "I CAN'T DO ANYTHING WITH DMs" is necessary
# soo... let's make it shitpost :)

user_data = dict() # temporary storage, cuz in this case there's no need for permanent one. It's mostly shitpost afterall
# user_data[user_id] = index_of_sequential_response
responses_sequential = []
responses_random = []

#####################################################################################################

# API for bundle
def AddSequentialResponse(response):
    responses_sequential.append(response)
def AddRandomResponse(response):
    responses_random.append(response)

#####################################################################################################

def FetchResponse(user):
    if user.id not in user_data: user_data[user.id] = 0
    if user_data[user.id] < len(responses_sequential):
        index = user_data[user.id]
        user_data[user.id] = user_data[user.id] + 1
        return responses_sequential[index]
    else:
        if len(responses_random) > 0:
            return random.choice(responses_random)
        else:
            return None

async def on_dm(message):
    user = message.author
    response = FetchResponse(user)
    if response:
        response = response.replace("USER", user.mention)
        response = response.replace("NAME", user.name)
        await message.channel.send(response)
triggers.on_dm.append(on_dm)

#####################################################################################################

