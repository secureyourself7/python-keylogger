#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os                  # for handling paths
import sys                 # for getting sys.argv and reading multiple line user input
import time
import tkinter as tk
from tkinter.filedialog import askopenfilename
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_OAEP
from Cryptodome.Hash import SHA3_512
import base64
import getpass             # for securely entering a user's pass phrase to access the private key

# - GLOBAL SCOPE VARIABLES start -

module_path = os.path.abspath(__file__)
dir_path = os.path.dirname(module_path)

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


# CHOOSE AN ENCRYPTED LOG FILE
tk.Tk().withdraw()  # we don't want a full GUI, so keep the root window from appearing
encrypted_log_filename = askopenfilename(title="CHOOSE YOUR ENCRYPTED LOG FILE",
                                         filetypes=[("All Files", "*.*")],
                                         initialdir=dir_path, multiple=False)
if encrypted_log_filename == "":
    exit()
# CHOOSE A PRIVATE KEY FILE
private_key_filename = askopenfilename(title="CHOOSE YOUR PRIVATE KEY FILE (*.pem)",
                                       filetypes=[("PEM files", "*.pem")],
                                       initialdir=dir_path, multiple=False)
if private_key_filename == "":
    exit()

# decrypt log
with open(encrypted_log_filename, "rb") as f:
    encrypted_log_str = f.read()
    if os.name == 'nt':
        clear = lambda: os.system('cls')    # on Windows System
    else:
        clear = lambda: os.system('clear')  # on Linux System
    clear()
    passphrase = getpass.getpass(prompt='\nEnter your private key passphrase:\n')
    with open(private_key_filename, "rb") as f:
        private_key = f.read()
        print('Decryption started...')
        decrypted_log = decrypt_many(encrypted_log_str, private_key, passphrase)
    del private_key

# save decrypted log:
new_filename = ".".join(encrypted_log_filename.split(".")[:-1]) + "_decrypted.txt"
with open(new_filename, "w") as f:
    f.write(decrypted_log)
del decrypted_log

erase = input('Finished! Saved to ' + new_filename + '. \nClear the console output? (y / n)')
if erase.lower() == 'y':
    clear()
    print('cleared')
    time.sleep(5)
