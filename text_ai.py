import requests
from dotenv import load_dotenv # ENV vars
import os
from serpapi import GoogleSearch

import cmd
import data
import log
import triggers
import tools

load_dotenv()
DEEP_AI_KEY = os.getenv('DEEP_AI_KEY') if os.getenv('DEEP_AI_KEY') else 'quickstart-QUdJIGlzIGNvbWluZy4uLi4K'
SERP_API_KEY = os.getenv('SERP_API_KEY') if os.getenv('SERP_API_KEY') else '0445874b278bd06c93f6db60d5ee4095c406a7bf8264c6884ec1ba741dcf5f0a'

##################################################################################################

GENERATE_API = "https://api.deepai.org/api/text-generator"
SUMMARIZE_API = "https://api.deepai.org/api/summarization"
TAG_API = "https://api.deepai.org/api/text-tagging"

def deep_ai(api, text):
    r = requests.post(
        api,
        data={
            'text': text,
        },
        headers={'api-key': DEEP_AI_KEY}
    )
    return r.json()

def serp_google_question(text):
    params = {
      "q": text,
      "hl": "en",
      "gl": "uk",
      "api_key": SERP_API_KEY
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    if 'answer_box' in results:
        return results['answer_box']
    return None
    
##################################################################################################

async def deep_ai_status(): # i think there's no need to check on all of them, one is enough
    try:
        text = "Why hello there!"
        a = deep_ai(GENERATE_API, text)['output']
        return True
    except:
        return False
triggers.Status.append( ("Deep AI integration", deep_ai_status) )

async def serp_api_status():
    try:
        text = "Age of universe"
        a = serp_google_question(text)
        if a:
            return True
        else:
            return False
    except:
        return False
triggers.Status.append( ("Serp API integration", serp_api_status) )

##################################################################################################

def Generate(text):
    try:
        return deep_ai(GENERATE_API, text)['output']
    except Exception as e:
        log.write(e)
        return "Error occured :c"

def Summarize(text):
    try:
        return deep_ai(SUMMARIZE_API, text)['output']
    except Exception as e:
        log.write(e)
        return "Error occured :c"

def Tag(text):
    try:
        return deep_ai(TAG_API, text)['output']
    except Exception as e:
        log.write(e)
        return "Error occured :c"

def SearchGoogle(text):
    try:
        r = serp_google_question(text)
        if r:
            if r['type'] == 'organic_result':
                output = r['title'] + "\n" + r['snippet'] + "\n" + r['link']
                return output
            return "Unsupported type of result: " + r['type']
        else:
            return "No answer found for: " + text
    except Exception as e:
        log.write(e)
        return "Error occured :c"

##################################################################################################

async def ProcessAndRespond(function, message, base_text):
    english_text = tools.EnsureEnglish(base_text)
    generated_text = function(english_text)
    for out in tools.segment_text(generated_text, 1980): await message.reply("```" + out + "```", mention_author=False)
    
##################################################################################################

async def cmd_deep_ai(function, ctx, args):
    if len(args) > 0:
        text = ' '.join(args)
    elif ctx.message.reference:
        message = ctx.message.reference.resolved
        text = message.content
    else:
        raise RuntimeError("Looks like you forgot to attach starting text")
    await ProcessAndRespond(function, ctx.message, text)
    return True

async def cmd_ask(ctx,args):
    text = ' '.join(args)
    answer = SearchGoogle(text)
    for out in tools.segment_text(answer,1980): await ctx.message.reply(out, mention_author=False)
    return True

parser = cmd.Parser()
cmd.Add(parser, "generate", lambda ctx, args: cmd_deep_ai(Generate, ctx, args), "Generate text based on sample.", "")
cmd.Add(parser, "summarize", lambda ctx, args: cmd_deep_ai(Summarize, ctx, args), "Autosummarize text", "")
cmd.Add(parser, "tag", lambda ctx, args: cmd_deep_ai(Tag, ctx, args), "Tag keywords in text", "")
cmd.Add(parser, "ask", cmd_ask, "Ask questions to Google", "")
    
cmd.Add(cmd.parser, "text", parser, "Tools to generate or process text. Only English.", "")

##################################################################################################

