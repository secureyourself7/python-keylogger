#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os                  # for handling paths and removing files (FTP mode)
import sys                 # for getting sys.argv
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA3_512
import base64
import getpass             # for securely entering a user's pass phrase to access the private key

# - GLOBAL SCOPE VARIABLES start -

full_path = os.path.dirname(os.path.realpath(sys.argv[0]))

# RSA KEYS FOR ENCRYPTION. Use the commands at the bottom of this script to generate a new key pair.

# private key for testing purposes only!
private_key_str = """-----BEGIN PRIVATE KEY-----
Proc-Type: 4,ENCRYPTED
DEK-Info: DES-EDE3-CBC,43A5A1A3E59DAC43

Kpk2sD0GYp6nTCOmdgkW8xiseM7U/91gxmwXiBUmChJ5q3MAlrul3iv0IJYJ4wnO
BJYgsIJGsHc6s4a++QoI+a/pNGjhwxnObhDAJflzAl9PBRBewC41L9sSgUPOF+WR
pNU+g6/XKQcaSiaPFVNMquJWIRp9VrtM3O0dUp5CXZ1Nj3SRE73RW6vpYsJ4Hrfm
I0G7CWWbZGZdIjCh+u6LVdimdaq4sl56vTByvjhDj7fSQS+djY467cTpWShrDSUU
ngr2nFFDWwRyBOiiQpRYKwrcGpfAnwuR94oO4bAhSfUrm1jrkEk9VKVQroUErJWf
3DNTg9lm6WPzZALS9Vm+W8grDYJDvuhwja62GGy2v0LpWHqL/s6/uznz22O/wgxu
dOeWIcuobI0MTPghcHZPH04+xfOB1rV3WPq6RYH88KpGqf7zTLi9g6TlLWyqOXr3
CZrGStWeLptoH2S7zWx7EPfm9wo0HDsXG4nzZEtPxaGfWZXzvlIBghsQuwvDS3oz
nm+YZXX5qvsJXOCSIEXyEYXQqmsX8JAI4a8LEj67/ohFVAj+ZSd3XAuFHHk8a0L9
O1ZDyLyDjcwGgNVCV2uE25aoKgy60kqKSTdO7bpXbxrLn1Up5wRGEvx68/7uyqiE
ckm7eU0JCh8K8qmci+Nwmn8+0eOPafVWL36uHmNuqC7kRzzJxOXMUC7MxgP45Guf
xyAswrJZ/VzJ290ukFunHRCKJW1EOXBbEzopL3kcLeK8rL61VuVE7u7Po4ocS1nW
hBOunpUp6MD5VOc6hBOKi05k+a6iuz+2UElNvAtiTn4NcodM2Yz7bAp5hNFJTUZt
dux9RT7UL7rTps6MxkMUTIwS0LOE0SjcvWRvnBHI3ydjnbij9610AIxp6C/Wbz6Q
uMF7Yim5jjtW9eda+yTgBHasY1hZ1UezfXNHHxmDupnPsoFltHXwy2Mj4oGKEvET
RAL4aiU6j2mHXSvVaD4/OB0pWuP9gMOQeTuELEPgYZSr9KZ+xuYHBVFtCcsW+SHj
+MVtsmhM9H77iUaJ8n5CVxmQXh6ad+mFUfdO5z+m3ozfdWlu6CPdOUNhNqynstL4
BhLaUA+J/vXw2vw2s/gM+nf2lNPIKVJQYZ1uSX/5FOVEX0U7cyWb67ACHrfLbyes
s3xI6B1/ultjESE4zaE82UrY+Ws6OG+toNrGEIkon264VyEiBLnUP2QxAtFk1LtD
k4G/DZcTfqnRI9iVJMeuo+4k2l/xBLcGP/zH4/cNQR6l/DGUhOmmeQKWQg/LjgKa
8+gw/el+bVdrZjk8N8vuZwn5NSRnYaSVBFJhUoljexSJ1MJ45KT9k0/Ejc2+E65E
N/lKABfkTrL0lzzsNiqrk7GEk7S9WGkeS7IoudCWj1p1dNWVkbkReIktHCMm33LM
QnOf0ckZfejgQ7QcMwn2/oqLeCPw4c1Sl5iqMBg2aVrKcLBUklsqfx4rOC3Mjom/
AcNRnxj9wvuCkqMbIsk89S4AXSStei34tKeOWiahaNdH67cygSC2qZELN+R5nfIa
dLd4qJn2I4xA0jpnfCLrqNW08CeOtHOKEIHgQQcc/wU8KmXOY6Wz5TqdqMOWSG9U
kI4hv8eGAeM5F61qRyUYebsWBa2qfE4WvqYuMl9CvJszpT/+SedeheEox4o+g1II
KbY6JlDd8taMWDgArSsnko+HxOW2v1Tu2mzjNRUYmyf5rjDnsP8bzSO50CeWxSgZ
+wzWOZznv1c3+o/VEKnyK/veHoBxlBU+ideMLjY+1qqDHFjv11XI4tOcHvXSBrxg
vNAGbhaMRx4SrXZWw+0PctasbGUkV5P1TbRRRy4DhLm0Ao5NdMrBJNlIpImhsSRl
i+lD8qtOZaAG5jG6MYwCimBCBCN8CVn+7jP+BrGB2HSDPv2o2ieEoZxeZh9XwNnT
h8vEVllw2jcNjKvcB0Vh6RA5OL4wHYJ3C6qrz4WN5tZvZY8Ba1KOKlaYrGkkf2lu
dStz1A4l6fep4uxchh0MOe2XYvE3xv5MRptTI+CTjCPeh9J8gW5Iz76TxhqnBl7Y
AgypY/CnY2KmkN3SLqiNv5jdJdn8LUCJCKCtGnIfdmP76xxzzdFgLGENWjybJFfv
ZFJwIc0zyFau1USiIqtTcVX3F8G3SUimGOXdpTJZ88obOl4TN7G23UtyoQCLbb5M
rStGENA2suU8X3lX3pV6Fzp9QPtrbBEKpNGSIO7EjuNxBkj6677yKiE0ZZVgjAzp
tu3YseP7Rcv4vUs3jSBRd0wzhoa7KHtS9FJeEsok+TAEOutdcvKqaias2eW0gaR/
+N7OJZiyQ29iVS/kiOWeo+DmrXYl6n+2dgTAh5lsAZXfv2FwQAlHpvZWZwKa8Mvc
Iplw2/plUAPvlmkkqjfBHAIKTL+4I1NpUkQzHTehCiK3VRLhWHzqduMWil6Bjy3h
Vv0DTsNnJxfjFT3e7a1fRSTT86AcawLK3+XU0/rJsdvN8wOFybiWfUHYituhcY1r
YZ2JthAbr+frILLqB/yyf9E/ZJt7pwySqPXxNkXjYnOl2Eh5BCTaf34VpIJ5SoB4
Lpo7fkOijkaOkj1l6SViLE2uIq0FEbo6MewNKSwLeucIVUXUwANjUx/jCiVOw0gq
13y4kHvW9bvLEOrmAxF9M6m+KUxIYOUsw+fLthZINrOpdsGVMYWK8wHx3PyHYqKc
fMBNwt2QI6gbfWHBExJ5FJRhHH4KJw8xPZtxVAXGlUGh5ZxqooVn88gjwg/ql+oD
FRzR2v4RGfJQCJVWOWWKDAhJ2b89auGL7wNzHFI6rXUF7Ipzhd0O0s6QKXs22FK6
MfAEs1s9Z4sHpbC5Fc2hvxenGQ6cPqXM4UZT5XCuzdi5mh3PkbKt+dy5/iCwHWns
WQiQAB13cLxiC/gsogKW1Jz565TO9KSY5+gZsykSiv95ayKkTCeRJIHPaQWABcET
0ypSqb8LCKmI7OGFxDm1AiXHkqutwOE0+x1mXcC3/U5iNALb2N5AF6cVLQXVE6/0
P/X5O/wtnRzQcGb+Z20cImvdZxeEbuabEiYCWkE9MwTcQP1itD7zsshXEqaeZmh/
hIddB+p6E0g95LBj5LEeZym7GkuFlEMyZU0mKgOPK76VNyEAOZqTN6RN4GEvVs2R
jov/2RKescJWOnXUg2kTHMnrsjYvtRjn
-----END PRIVATE KEY-----"""
private_key = bytes(private_key_str, 'utf-8')
# with open("private_key.pem", "rb") as f:
#     private_key = f.read()

# - GLOBAL SCOPE VARIABLES end -


def decrypt(encrypted_blob, passphrase=None):
    # Debug only
    global private_key
    key = RSA.importKey(private_key, passphrase)
    cipher = PKCS1_OAEP.new(key, hashAlgo=SHA3_512)
    # Base 64 decode the data
    encrypted_blob = base64.b64decode(encrypted_blob)
    decrypted_message = cipher.decrypt(encrypted_blob)
    del key, cipher  # do at least this as soon as possible
    return decrypted_message


def decrypt_many(encrypted, passphrase=None):
    if passphrase == '':
        passphrase = None
    delimiter = '---END---'
    if isinstance(encrypted, bytes):
        encrypted = encrypted.decode('utf-8')
    # remove the line breaks and ---START---
    encrypted = encrypted.replace('\n', '')
    encrypted = encrypted.replace('---START---', '')
    encrypted_split = encrypted.split(delimiter)
    # filter the empty elements
    encrypted_messages = [k for k in encrypted_split if len(k) > 0]
    # decrypt each message
    decrypted_blob = '\n'.join([decrypt(bytes(m, 'utf-8'), passphrase).decode('utf-8') for m in encrypted_messages])
    return decrypted_blob


# UNCOMMENT THIS TO READ ENCRYPTED LOGS (passphrase for the private key above - 'pass'):
test_string = """
---START---.......---END---
---START---.......---END---
"""
passphrase = getpass.getpass(prompt='Enter your private key passphrase')
print('decrypted log: ', decrypt_many(test_string, passphrase))

# UNCOMMENT THIS TO GENERATE NEW RSA PUBLIC-PRIVATE KEY PAIR:
"""
passphrase = getpass.getpass(prompt='Enter your private key passphrase')
new_key = RSA.generate(4096)
export_format = 'PEM'
private_key = new_key.exportKey(pkcs=8, passphrase=passphrase)
public_key = new_key.publickey().exportKey(format=export_format)
with open("private_key." + export_format.lower(), "wb") as f:
    f.write(private_key)
with open("public_key." + export_format.lower(), "wb") as f:
    f.write(public_key)
"""
