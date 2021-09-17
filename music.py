
import file
import temp
import data
import random
import pytube

################################################################################

music_dir = "music"
data.NewGuildEnvAdd("music_queue", [])
    
old_save = data.OnSaveTrigger
def SaveHook(local_env):
    global old_save
    local_env["music_queue"] = []
    return old_save(local_env)
data.OnSaveTrigger = SaveHook

################################################################################

def GetMusicDir():
    out = temp.GetTempDir() + music_dir
    file.EnsureDir(out)
    return out + "/"

def DownloadAudio(obj, dir): # obj - YouTube object
    filename = file.HashName(' ' + obj.title)
    if filename in file.ListOfFiles(dir):
        return filename
    streams = obj.streams
    stream = streams.filter(type='audio').get_audio_only()
    stream.download(output_path=dir, filename=filename, max_retries=10)
    return filename

def Shuffle(local_env):
    random.shuffle(local_env["music_queue"])

def Fetch(local_env):
    local_queue = local_env["music_queue"]
    if len(local_queue) > 0:
        return local_queue.pop(0)
    return None

################################################################################
