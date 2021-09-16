
import file
import temp
import data
import random
import pytube

################################################################################

music_dir = "music"
data.NewGuildEnvAdd("music_queue", [])

################################################################################

def GetMusicDir():
    out = temp.GetTempDir() + music_dir
    file.EnsureDir(out)
    return out + "/"

def DownloadAudio(url, dir):
    obj = pytube.YouTube(url)
    filename = str(hash(' ' + obj.title))
    if filename in file.ListOfFiles(dir):
        return filename
    streams = obj.streams
    stream = streams.filter(type='audio').get_audio_only()
    stream.download(output_path=dir, filename=filename, max_retries=10)
    return filename
################################################################################
