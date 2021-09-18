from pickle import load
from pickle import dump
import os
import os.path
import hashlib

# by Jakub Grzana

# function to load Python object from file
# input: filename - string, name of file
# output: Python object loaded from file
def Load(filename):
	input = open(filename, 'rb')
	bin = load(input)
	input.close()
	return bin

# function to save Python object to file
# input: filename - string, name of file 
# input: bin - python object to be saved
# output: None
def Save(filename,bin):
	output = open(filename, 'wb')
	dump(bin, output, -1)
	output.close()

def EnsureDir(dir):
    if not os.path.isdir(dir):
        os.mkdir(dir)

def PurgeDir(dir):
    if os.path.isdir(dir):
        shutil.rmtree(dir)

def Exist(filepath):
    return os.path.isfile(filepath)

def ListOfFiles(path):
    return [ f for f in os.listdir(path) if os.path.isfile( os.path.join(path, f) ) ]

def Hash(name):
    encoded = str(name).encode()
    return hashlib.md5(encoded).hexdigest()