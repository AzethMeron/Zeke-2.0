

#####################################################################################################

# Universal tools

import hashlib
import requests
import string
import random

def Success(chance):
    rand = random.randint(1,100)
    return (rand <= chance)

def Hash(name):
    encoded = str(name).encode()
    return hashlib.md5(encoded).hexdigest()
    
def is_url(string):
    try:
        response = requests.get(string)
        return True
    except:
        return False
    
def flatten(_lists):
    return [item for sublist in _lists for item in sublist]

def size_args(args, default_min, default_max, hard_min, hard_max):
    num_min = default_min
    num_max = default_max
    if len(args) == 1:
        num_max = max(1, int(float(args[0])))
    if len(args) == 2:
        min_arg = min(int(float(args[0])), int(float(args[1])))
        max_arg = max(int(float(args[0])), int(float(args[1])))
        num_min = max(1, min_arg) - 1
        num_max = max(1, max_arg)
    num_min = max(num_min, hard_min)
    num_max = min(num_max, hard_max)
    return (num_min, num_max)

def list_size_args(args, olist, default_min, default_max):
    return size_args(args, default_min, default_max, 0, len(olist))

def random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k = length))  

def wrap_code(string):
    return f"```{string}```"

def wrap_bold(string):
    return f"**{string}**"

def wrap_itallic(string):
    return f"*{string}*"

def link_to_message(guild_id, channel_id, message_id):
    return f"https://discordapp.com/channels/{guild_id}/{channel_id}/{message_id}"

#####################################################################################################

# Text processing tools

import nltk
nltk.download('wordnet') 
#nltk.download('averaged_perceptron_tagger')
from nltk.stem import WordNetLemmatizer

def load_file_as_lines(filename):
    with open(filename, "r") as file:
        lines = file.readlines()
        return [line.rstrip() for line in lines if len(line.rstrip()) > 0 and line.rstrip()[0] != '#' ]

def simple_normalisation(text, stopwords): # stopwords - set of strings, if you use list, it has negative impact on performance
    no_punctuation = remove_punctuation(text)
    return " ".join([ word for word in no_punctuation.lower().split() if word not in stopwords ])
ENGLISH_STOPWORDS = set(load_file_as_lines("english_stopwords.txt"))
ENGLISH_LEMMATIZER = WordNetLemmatizer()
def english_normalisation(text):
    words = simple_normalisation(text, ENGLISH_STOPWORDS).split()
    return " ".join([ENGLISH_LEMMATIZER.lemmatize(word) for word in words])

# [ (char_to_be_replaced, char_used_to_replace) ]
PUNCTUATION_LIST = [ 
('.',' '),
('?',' '),
('!',' '),
(',',' '),
(':',' '),
(';',' '),
('-',''),
('(',' '),
(')',' '),
('[',' '),
(']',' '),
("'",''),
('"','')
]
def remove_punctuation(text):
    for (mark,replacement) in PUNCTUATION_LIST:
        text = text.replace(mark, replacement)
    return text

def segment_text(string, length):
    return (string[0+i:length+i] for i in range(0, len(string), length))

def uppercase_segments(text):
    output = []
    trail = []
    words = remove_punctuation(text).split()
    for word in words:
        if word.isupper() and (len(word) > 1 or len(trail) > 0):
            trail.append(word)
        elif len(trail) > 0:
            output.append(" ".join(trail))
            trail.clear()
    if len(trail) > 0:
        output.append(" ".join(trail))
    return output

#####################################################################################################

# Language tools

from dotenv import load_dotenv # ENV vars
from deep_translator import GoogleTranslator
import detectlanguage # better but restricted by API key
import langdetect # worse but no restrictions
import os
import triggers

load_dotenv() # load environmental variables from file .env
detectlanguage.configuration.api_key = os.getenv('DETECT_LANGUAGE_TOKEN') if os.getenv('DETECT_LANGUAGE_TOKEN') else None

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

async def traslator_status():
    pl_text = "Dzisiaj jest piękny dzień. W dni takie jak te, dzieci twojego pokroju..."
    try:
        RawTranslate('pl', 'en', pl_text)
        return True
    except:
        return False
triggers.Status.append( ("Google translate integration", traslator_status) )

async def detect_status():
    pl_text = "Dzisiaj jest piękny dzień. W dni takie jak te, dzieci twojego pokroju..."
    detect = True if DetectLanguage(pl_text) == 'pl' else False
    return detect
triggers.Status.append( ("Detect language integration", detect_status) )