
import dropbox
import os
import pickle
from dotenv import load_dotenv # ENV vars

import triggers
import tools
import file
import log

# Ngl this solution is hacked into this bot
# but i think it is good enough

########################################################################################################

# Low-leve section
# NOTE: All files are stord in one directory
# Filename passed as argument should bd HASHED FILEPATH!!!

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

def raw_exist(filename):
    try:
        dbx.files_get_metadata('/' + filename)
        return True
    except:
        return False

def raw_remove(filename):
    dbx.files_delete('/' + filename)

async def raw_status():
    data = tools.random_string(10)
    filename = tools.random_string(5)
    try:
        raw_send(data, filename)
        recv = raw_get(filename)
        raw_remove(filename)
        if data == recv: return True
        else: return False
    except:
        return False
triggers.Status.append( ("Storage integration",raw_status) )

########################################################################################################

def Save(var, filepath):
    if initialised():
        filename = tools.Hash(filepath)
        try:
            raw_send(var, filename)
        except Exception as e:
            log.write(e)

def Load(filepath):
    if initialised():
        filename = tools.Hash(filepath)
        if raw_exist(filename):
            try:
                return raw_get(filename)
            except Exception as e:
                log.write(e)
    return None

def Exist(filepath):
    if initialised():
        filename = tools.Hash(filepath)
        return raw_exist(filename)
    return False

########################################################################################################
    
def save_guild(local_env, filepath, filename):
    # Remote copy
    Save(local_env, filename)
    # Local copy
    file.Save(filepath, local_env)
    
def load_guild(filepath, filename):
    # Remote copy
    tmp = Load(filename)
    if tmp: return tmp
    # Local copy
    if file.Exist(filepath): return file.Load(filepath)
    # None if not found
    return None