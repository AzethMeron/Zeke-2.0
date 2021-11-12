import requests
from dotenv import load_dotenv # ENV vars
import os

import cmd
import data
import log
import triggers
import tools

load_dotenv()
DEEP_AI_KEY = os.getenv('DEEP_AI_KEY') if os.getenv('DEEP_AI_KEY') else 'quickstart-QUdJIGlzIGNvbWluZy4uLi4K'

##################################################################################################

def deep_ai_generate(text):
    r = requests.post(
        "https://api.deepai.org/api/text-generator",
        data={
            'text': text,
        },
        headers={'api-key': DEEP_AI_KEY}
    )
    return r.json()

def deep_ai_summarisation(text):
    r = requests.post(
        "https://api.deepai.org/api/summarization",
        data={
            'text': text,
        },
        headers={'api-key': DEEP_AI_KEY}
    )
    return r.json()

def deep_ai_tag(text):
    r = requests.post(
        "https://api.deepai.org/api/text-tagging",
        data={
            'text': text,
        },
        headers={'api-key': DEEP_AI_KEY}
    )
    print(r.json())

##################################################################################################

def generateStatus():
    try:
        text = "Why hello there!"
        tmp = deep_ai_generate(text)['output']
        return True
    except:
        return False
triggers.Status.append( ("Deep AI Text Generation", generateStatus) )

def summarisationStatus():
    try:
        text = "ERM means Event Related Model and is dedicated to Heroes3: Shadow of Death game and add-on. ERM is a new technology that makes possible dynamically changing the map objects' properties as a result of certain player's (including computer) actions. It essentially offers scripting (programing) posibility. Some default script files ensure WOG enhancements as described in the latest version info, but ERM also gives the basic game user access to creating its own scripts to add his own imagination and flavor to the game. It would be a good idea to start with the tutorials"
        tmp = deep_ai_summarisation(text)['output']
        return True
    except:
        return False
#triggers.Status.append( ("Deep AI Text Summarization", summarisationStatus) )

def taggingtatus():
    try:
        text = "ERM means Event Related Model and is dedicated to Heroes3: Shadow of Death game and add-on. ERM is a new technology that makes possible dynamically changing the map objects' properties as a result of certain player's (including computer) actions. It essentially offers scripting (programing) posibility. Some default script files ensure WOG enhancements as described in the latest version info, but ERM also gives the basic game user access to creating its own scripts to add his own imagination and flavor to the game. It would be a good idea to start with the tutorials"
        tmp = deep_ai_tag(text)['output']
        return True
    except:
        return False
#triggers.Status.append( ("Deep AI Text Tagging", taggingtatus) )

##################################################################################################

def Generate(text):
    try:
        return deep_ai_generate(text)['output']
    except Exception as e:
        log.write(e)
        return "Error occured :c"

def Summarize(text):
    try:
        return deep_ai_summarisation(text)['output']
    except Exception as e:
        log.write(e)
        return "Error occured :c"

def Tag(text):
    try:
        return deep_ai_tag(text)['output']
    except Exception as e:
        log.write(e)
        return "Error occured :c"

##################################################################################################

async def GenerateAndRespond(message, base_text):
    english_text = tools.EnsureEnglish(base_text)
    generated_text = Generate(english_text)
    for out in tools.segment_text(generated_text, 1980): await message.reply("```" + out + "```")

async def SummarizeAndRespond(message, base_text):
    english_text = tools.EnsureEnglish(base_text)
    summary = Summarize(english_text)
    for out in tools.segment_text(summary, 1980): await message.reply("```" + out + "```")
    
##################################################################################################

async def tmp_gen(ctx, args):
    text = ' '.join(args)
    await GenerateAndRespond(ctx.message, text)

parser = cmd.Parser()
cmd.Add(parser, "generate", tmp_gen, "", "")

async def command(ctx, args):
    return await cmd.Parse(parser, ctx, args)