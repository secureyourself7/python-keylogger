## Advanced Python Keylogger for Windows

NOTE: This project should be used for authorized testing or educational purposes only. 
You are free to copy, modify and reuse the source code at your own risk. 

### Uses

Some uses of a keylogger are:
- Security Testing: improving the protection against hidden key loggers
- Business Administration: Monitor what employees are doing (with their consent)
- School/Institutions: Track keystrokes and log banned words in a file.
- Personal Control and File Backup: Make sure no one is using your computer when you are away.
- Parental Control: Track what your children are doing.
- Self-analysis and assessment.

### Features
- Global event hook on all keyboards (captures keys regardless of focus) using [Keyboard](https://github.com/boppreh/keyboard)
- Pure Python, no C modules to be compiled.
- Human-readability of logs:
  - Logging keys as they actually are in your layout. Cyrillic keyboard layout is fully implemented. 
  - Logging window titles and current time where appropriate.
  - Backspace support (until the active window is changed).
  - Full upper- and lowercase detection (capslock + shift).
- Variety of logging modes:
  - Storing logs locally
  - Sending logs to Google Forms
  - Sending logs via email
  - Uploading logs via FTP
  - Debug mode (printing to console)
- Privacy and security: 
  - PGP public-key encryption of logs on the fly using [PyCrypto](https://www.dlitz.net/software/pycrypto/) (paste only your public key).
- Variable logging frequency (by default once every 100 new characters).
- Persistence:
  - Adding to Windows Startup.
  - Every 10 seconds making sure that a keylogger process is running.

### Getting started

#### System requirements
- MS Windows (tested on 10). TBD: add Linux and macOS.
- Python 3.7+: https://www.python.org/downloads/

#### Usage

##### **Quick start**
1. `pip install requirements.txt` (alternatively `python -m pip ...`)
1. `python logger_main.py local encrypt startup`

##### System arguments
`logger_main.py mode [encrypt] [startup]`
- **modes**:
  - **local:** store the logs in a file (e.g. 2019-Jan-01.txt)
  - **remote:** send the logs to a Google Form. You must specify the Form URL and Field Name in the script.
  - **email:** send the logs to an email. You must specify (SERVER, PORT, USERNAME, PASSWORD, TO)
  - **ftp:** upload logs file to an FTP account. You must specify (SERVER, USERNAME, PASSWORD, SSL (1 to enable, or 0), OUTPUT DIRECTORY)
- **[optional]**
  - **encrypt:** enable the encryption of logs with a public key provided in logger.py.
  - **startup:** add the keylogger to Windows startup.

### Video tutorials (similar but simpler projects)
https://www.youtube.com/watch?v=uODkiVbuR-g
https://www.youtube.com/watch?v=8BiOPBsXh0g

### Known issues
- See [Keyboard: Known limitations](https://github.com/boppreh/keyboard#known-limitations). 
Feel free to contribute to fix any problems, or to submit an issue!


### Notes
Cyrillic layout is implemented, meaning support for these languages: Russian, Russian - Moldava, Azeri, Belarusian, Kazakh, Kyrgyz, Mongolian, Tajik, Tatar, Serbian, Ukrainian, Uzbek. 

Please note, this repo is for educational purposes only. No contributors, major or minor, are responsible for any actions done by this program.

Don't really understand licenses or tl;dr? Check out the [MIT license summary](https://tldrlegal.com/license/mit-license).

Distributed under the MIT license. See [LICENSE](https://github.com/secureyourself7/python-keylogger/blob/master/LICENSE) for more information.
