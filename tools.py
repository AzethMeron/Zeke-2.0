
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