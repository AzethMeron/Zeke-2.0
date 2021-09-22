

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