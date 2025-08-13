#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
from Cryptodome.PublicKey import RSA
import getpass

full_path = os.path.dirname(os.path.realpath(sys.argv[0]))

passphrase_1 = getpass.getpass(
    prompt='Enter your private key passphrase (your input will be hidden):\n'
)

passphrase_2 = getpass.getpass(
    prompt='Confirm your private key passphrase (your input will be hidden):\n'
)

if passphrase_1 != passphrase_2:
    raise ValueError("Your inputs don't match!")

print('Inputs match, generating your keys...')

new_key = RSA.generate(4096)
export_format = 'PEM'

private_key = new_key.exportKey(
    pkcs=8,
    passphrase=passphrase_1
)

public_key = new_key.publickey().exportKey(
    format=export_format
)

with open(
    os.path.join(full_path, "private_key." + export_format.lower()), "wb"
) as f:
    f.write(private_key)

with open(
    os.path.join(full_path, "public_key." + export_format.lower()), "wb"
) as f:
    f.write(public_key)

print('Finished!')
