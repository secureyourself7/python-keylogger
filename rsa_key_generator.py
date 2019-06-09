#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os                  # for handling paths and removing files (FTP mode)
import sys                 # for getting sys.argv
from Crypto.PublicKey import RSA
import getpass             # for securely entering a user's pass phrase to access the private key

# - GLOBAL SCOPE VARIABLES start -
full_path = os.path.dirname(os.path.realpath(sys.argv[0]))
# - GLOBAL SCOPE VARIABLES end -

# GENERATE NEW RSA PUBLIC-PRIVATE KEY PAIR:
passphrase = getpass.getpass(prompt='Enter your private key passphrase')
new_key = RSA.generate(4096)
export_format = 'PEM'
private_key = new_key.exportKey(pkcs=8, passphrase=passphrase)
public_key = new_key.publickey().exportKey(format=export_format)
with open(os.path.join(full_path, "private_key." + export_format.lower()), "wb") as f:
    f.write(private_key)
with open(os.path.join(full_path, "public_key." + export_format.lower()), "wb") as f:
    f.write(public_key)
