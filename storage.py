
import dropbox
import os
import pickle
from dotenv import load_dotenv # ENV vars

import tools
import file
import log

# Ngl this solution is hacked into this bot
# Should be remade? prolly

########################################################################################################

load_dotenv() # load environmental variables from file .env
dbx = None
if os.getenv('DROPBOX_TOKEN'):
    dbx = dropbox.Dropbox(os.getenv('DROPBOX_TOKEN'))

def initialised():
    if dbx:
        return True
    else:
        return False

def raw_send(var, filename):
    data = pickle.dumps(var, -1)
    dbx.files_upload(data, '/' + filename, mute=True, mode=dropbox.files.WriteMode.overwrite)

def raw_get(filename):
    f, r = dbx.files_download('/' + filename)
    return pickle.loads(r.content)

def file_exist(filename):
    try:
        dbx.files_get_metadata('/' + filename)
        return True
    except:
        return False

########################################################################################################

def save(var, filepath):
    if initialised():
        filename = tools.Hash(filepath)
        try:
            raw_send(var, filename)
        except Exception as e:
            log.write(e)

def load(filepath):
    if initialised():
        filename = tools.Hash(filepath)
        if file_exist(filename):
            try:
                return raw_get(filename)
            except Exception as e:
                log.write(e)
    return None

########################################################################################################
    
def get_file(filename):
    if dbx:
        f, r = dbx.files_download('/' + filename)
        return pickle.loads(r.content)
    else:
        raise RuntimeError("Dropbox not activated")
    
def save_guild(local_env, filepath, filename):
    # Remote copy
    save(local_env, filename)
    # Local copy
    file.Save(filepath, local_env)
    
def load_guild(filepath, filename):
    # Remote copy
    try:
        return get_file(filename)
    except Exception as e:
        pass
    # Local copy
    if file.Exist(filepath):
        return file.Load(filepath)
    # None if not found
    return None