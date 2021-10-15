

#####################################################################################################

# Universal tools

import hashlib
import requests

def Hash(name):
    encoded = str(name).encode()
    return hashlib.md5(encoded).hexdigest()
    
def is_url(string):
    try:
        response = requests.get(string)
        return True
    except:
        return False

def segment_text(string, length):
    return (string[0+i:length+i] for i in range(0, len(string), length))

def list_size_args(args, _list, default_min, default_max):
    num_min = default_min
    num_max = default_max
    if len(args) == 1:
        num_max = max(1, int(float(args[0])))
    if len(args) == 2:
        min_arg = min(int(float(args[0])), int(float(args[1])))
        max_arg = max(int(float(args[0])), int(float(args[1])))
        num_min = max(1, min_arg) - 1
        num_max = max(1, max_arg)
    num_min = max(num_min, 0)
    num_max = min(num_max, len(_list))
    return (num_min, num_max)

#####################################################################################################

# Language tools

from dotenv import load_dotenv # ENV vars
from deep_translator import GoogleTranslator
import detectlanguage # better but restricted by API
import langdetect # worse but no restrictions
import os

load_dotenv() # load environmental variables from file .env
detectlanguage.configuration.api_key = os.getenv('DETECT_LANGUAGE_TOKEN')

def RawTranslate(src_lang, tgt_lang, text):
    return GoogleTranslator(source=src_lang, target=tgt_lang).translate(text)

def Translate(tgt_lang, text):
    src_lang = DetectLanguage(text)
    translated = text
    try:
        if src_lang != tgt_lang:
            translated = RawTranslate(src_lang, tgt_lang, text)
    except:
        pass
    return (src_lang, tgt_lang, translated)

def DetectLanguage(text):
    try:
        return detectlanguage.simple_detect(text)
    except:
        try:
            return langdetect,detect(text)
        except:
            pass
    return 'auto'

def EnsureEnglish(text):
    output = text
    try:
        output = RawTranslate('auto', 'en', text)
    except:
        pass
    return output

#####################################################################################################