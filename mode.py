
from multiprocessing import Process
from multiprocessing import Queue

import triggers
import data

################################################################################

data.NewGuildEnvAdd("mode_threshold", 0.49)

def GetThreshold(local_env):
    return local_env["mode_threshold"]

################################################################################

import profanity_check

def profanity(text):
    if profanity_check.predict([text]) == [1]:
        return True
    return False

################################################################################

tests = [] # (name, queue_in, queue_out, weight)
processes = [] # reduntant but, who knows

import threading # protection against race in communication with subprocesses. Not sure if it's necessary
lock = threading.Lock()
def Lock():
    global lock
    lock.acquire()
def Release():
    global lock
    lock.release()

def CheckProcess(qi, qo, func):
    while True:
        text = qi.get()
        result = False
        try:
            result = func(text)
        except:
            pass
        qo.put(result)

# Add check for specific type of hate speech
def AddCheck(name, func, weight): # bool func(text)
    qi = Queue()
    qo = Queue()
    tests.append((name, qi, qo, weight))
    p = Process(target=CheckProcess, args=(qi, qo, func,))
    p.start()
    processes.append(p)

################################################################################

# Run tests
def GetResults(text):
    output = []
    Lock()
    for (_1, qi, _q, _2) in tests:
        qi.put(text)
    for (name, qi, qo, weight) in tests:
        result = qo.get()
        output.append( (name, result, weight) )
    Release()
    return output

# Get weighted average
def GetAverageResults(results):
    sum = 0
    total_weight = 0
    for (name, result, weight) in results:
        sum = sum + int(result) * weight
        total_weight = total_weight + weight
    return sum / total_weight

################################################################################

def OnInit(bot):
    AddCheck("offensive language", profanity, 10)
triggers.OnInitTrigger.append(OnInit)

async def OnMessage(local_env, message, normalised_text):
    results = GetResults(normalised_text)
    avg_results = GetAverageResults(results)
    if avg_results > GetThreshold(local_env):
        await HatefulMessageDetected(local_env, message, normalised_text, results, avg_results)
triggers.on_message.append(OnMessage)

################################################################################

async def HatefulMessageDetected(local_env, message, normalised_text, results, avg_results):
    pass