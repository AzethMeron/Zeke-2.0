
# by Jakub Grzana

# 16byte key means 2^128 possibilities, over 10^38. According to internet, it's still safe.
# Encrypted data is bytearray, can be easily saved to file
# In encrypted data, IV key and hash (sha256) of data is stored, and validity of this data is checked on decryption
# Also i've 0 education in safety and encryption. I hope im doing it right.

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
import pickle
import hashlib

####################################################################################################################

def GenerateKey(bytelength=16):
    if bytelength not in {16,24,32}: raise RuntimeError("Incorrect bytelength for AES encryption: " + str(bytelength))
    return get_random_bytes(bytelength)

def PasswdToKey(passwd, bytelength=16):
    salt = b'\x01\xebQXs\xc2\x17\xe9\xbbh\xa1\xabH\x96^K\x06\xe5:\x84"Z\xfc>a\xb49\x97ng\x90\x04\xff\x80\x9b\x8a\x01\xa5%\xb7\x03\xcc\xc7\x94\x1a3\xbeP\x9e\xc4\xa5\x05\xd7VD\xa7\xdd4\x90y\xa1lP\xc6'
    key = PBKDF2(passwd, salt, dkLen=bytelength)
    return key

def Encrypt(key, var):
    iv = GenerateKey(16)
    coder = AES.new(key, AES.MODE_CFB, iv=iv)
    data = pickle.dumps(var, -1)
    hash = hashlib.sha256(data).hexdigest()
    cipher = coder.encrypt(data)
    dump = pickle.dumps((iv, cipher, hash), -1)
    return dump
    
def Decrypt(key, dump):
    (iv, cipher, hash) = pickle.loads(dump)
    coder = AES.new(key, AES.MODE_CFB, iv=iv)
    data = coder.decrypt(cipher)
    if hashlib.sha256(data).hexdigest() != hash:
        raise RuntimeError("Incorrect hash, which most likely means tampering with cipher or incorrect decryption")
    var = pickle.loads(data)
    return var

####################################################################################################################