Speech To Text (OpenAI) Chat 
=========
## Setup Instructions (Mac OS)



Requirements
------------

#### Prerequisite

 1. Install Portaudio
```bash
brew install portaudio

```
2. Install Python venv
```bash
sudo apt install python3-venv

```

#### Installation Steps

1. Create new virtual environment
 ```bash
 python3 create_env.py
 ```

2. Activate virtual environment
```bash
 source venv/bin/activate
```

3. Upgrade Pip and Setuptools Packages
```bash
 pip install --upgrade pip setuptools
```

4. Install application
```bash
 pip install -e .
```

5. Update `API_KEY` variable in the `.env` file with your OpenAI Api Key.
```bash
API_KEY=<enter api key here>
```

Operations
--------------
#### Parameters
```bash
Input Variables:

- `-d, --duration`: (Required) [int]
  - Set the lenght of time to listen to user voice input.
- `-f --filename`: (Required) [str]
  - Set the conversation file.

```
#### Command
```bash
speech-to-text-openai-chat --duration 10 --filename test.txt
or
speech-to-text-openai-chat -d 10 -f test.txt
```


Bugs
--------------
```bash
SSL BUG
Warning: 

NotOpenSSLWarning: urllib3 v2.0 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020

Fix:
pip install urllib3==1.26.6
```

```bash
ERROR:
AttributeError: 'super' object has no attribute 'init' BUG

Fix:
replace: self = super(NSSpeechDriver, self).init() comment this line , and add the following
insert: self = objc.super(NSSpeechDriver, self).init()
```
License
-------

BSD

Author Information
------------------

Perrie Russell (@prussCoding)