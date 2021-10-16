
import dropbox
import os
import pickle
from dotenv import load_dotenv # ENV vars

import tools
import file
import log

# Ngl this solution is hacked into this bot
# Should be remade? prolly

load_dotenv() # load environmental variables from file .env
dbx = None
if os.getenv('DROPBOX_TOKEN'):
    dbx = dropbox.Dropbox(os.getenv('DROPBOX_TOKEN'))

def send_file(filedata, filename):
    if os.getenv('DROPBOX_TOKEN'):
        data = pickle.dumps(filedata, -1)
        dbx.files_upload(data, '/' + filename, mute=True, mode=dropbox.files.WriteMode.overwrite)
    
def get_file(filename):
    if os.getenv('DROPBOX_TOKEN'):
        f, r = dbx.files_download('/' + filename)
        return pickle.loads(r.content)
    
def save_guild(local_env, filepath, filename):
    # Local copy
    file.Save(filepath, local_env)
    # Remote copy
    try:
        send_file(local_env, filename)
    except:
        pass
    
def load_guild(filepath, filename):
    # Local copy
    if file.Exist(filepath):
        return file.Load(filepath)
    # Remote copy
    try:
        return get_file(filename)
    except Exception as e:
        pass
    # None if not found
    return None