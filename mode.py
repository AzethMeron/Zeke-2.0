
import triggers
import data

################################################################################

# Here goes data

################################################################################

import profanity_check

def profanity(text):
    if profanity_check.predict([text]) == [1]:
        return True
    return False

################################################################################

tests = [] # (name, func, weight)

# Add check for specific type of hate speech
def AddTest(name, func, weight): # bool func(text)
    tests.append( (name, func, weight) )

AddTest("offensive language", profanity, 10)

################################################################################

# Run tests
def RunTests(text): # return [ (name, result, weight) ]
    output = []
    for (name, func, weight) in tests:
        try:
            result = func(text)
        except:
            result = False
        output.append( (name, result, weight) )
    return output

# Get weighted average
def GetAverageResults(results):
    sum = 0
    total_weight = 0
    for (name, result, weight) in results:
        sum = sum + int(result) * weight
        total_weight = total_weight + weight
    if total_weight == 0: return 0
    return sum / total_weight

################################################################################

async def OnMessage(local_env, message, normalised_text):
    results = RunTests(normalised_text)
    avg_results = GetAverageResults(results)
    if avg_results:
        await HatefulMessageDetected(local_env, message, normalised_text, results, avg_results)
triggers.on_message.append(OnMessage)

################################################################################

async def HatefulMessageDetected(local_env, message, normalised_text, results, avg_results):
    pass