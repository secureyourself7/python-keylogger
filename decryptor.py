#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os                  # for handling paths
import sys                 # for getting sys.argv and reading multiple line user input
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA3_512
import base64
import getpass             # for securely entering a user's pass phrase to access the private key

# - GLOBAL SCOPE VARIABLES start -

full_path = os.path.dirname(os.path.realpath(sys.argv[0]))

# - GLOBAL SCOPE VARIABLES end -


def decrypt(encrypted_blob, private_key, passphrase=None):
    # Debug only
    key = RSA.importKey(private_key, passphrase)
    cipher = PKCS1_OAEP.new(key, hashAlgo=SHA3_512)
    # Base 64 decode the data
    encrypted_blob = base64.b64decode(encrypted_blob)
    try:
        decrypted_message = cipher.decrypt(encrypted_blob)
    except ValueError:
        decrypted_message = bytes('\n- Message decryption error -\n', 'utf-8')
    del key, cipher  # do at least this as soon as possible
    return decrypted_message


def decrypt_many(encrypted_log, private_key, passphrase=None):
    if passphrase == '':
        passphrase = None
    delimiter = '---END---'
    if isinstance(encrypted_log, bytes):
        encrypted_log = encrypted_log.decode('utf-8')
    # remove the line breaks and ---START---
    encr_log_str2 = encrypted_log.replace('\n', '')
    encr_log_str3 = encr_log_str2.replace('---START---', '')
    encrypted_split = encr_log_str3.split(delimiter)
    # filter the empty elements
    encrypted_messages = [k for k in encrypted_split if len(k) > 0]
    # decrypt each message
    decrypted_blob = '\n'.join([decrypt(bytes(m, 'utf-8'), private_key, passphrase).decode('utf-8')
                                for m in encrypted_messages])
    return decrypted_blob


# READ ENCRYPTED LOGS:
# RSA KEYS FOR ENCRYPTION
# private key
private_key_filename = input("ENTER YOUR PRIVATE KEY FILENAME OR FULL PATH (*.pem):\n")
try:
    with open(os.path.join(full_path, private_key_filename), "rb") as f:
        private_key = f.read()
except:
    with open(private_key_filename, "rb") as f:
        private_key = f.read()

print("""PASTE YOUR ENCRYPTED LOG/MESSAGE AND PRESS CTRL+D or CTRL+Z (for Windows), then ENTER. SHOULD LOOK LIKE THIS:
---START---.......---END---
---START---.......---END---\n""")
encrypted_log = []
while True:
    try:
        line = input()
    except EOFError:
        break
    encrypted_log.append(line)
encrypted_log_str = ''.join(encrypted_log)
clear = lambda: os.system('cls')  # on Windows System
# clear = lambda: os.system('clear')  # on Linux System
clear()
print('messages received\n')
passphrase = getpass.getpass(prompt='\nEnter your private key passphrase:\n')
print('Your decrypted log/message:\n', decrypt_many(encrypted_log_str, private_key, passphrase))
erase = input('Clear the console output? (y / n)')
if erase.lower() == 'y':
    clear()
    print('cleared')
