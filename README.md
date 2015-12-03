# Cardboardbot

A Jabber chatbot with a bunch of uses

## Requirements

Might work with Python 3, but has only been tested with Python 2.7

You can install the required Python 2.7 packages with a simple
`pip install -r requirements_python2.txt`

There's also a list of Python 3 requirements you can install with
`pip install -r requirements_python3.txt`

You will also need an AIML library for the bot to use, at least in Python 2.7. I personally used the
[A.L.I.C.E. AIML set](https://code.google.com/p/aiml-en-us-foundation-alice/)
which works nicely. This isn't needed for Python 3.

## Usage

Create your own `config.py` based on the example provided. Give your bot some
personality by creating a personality file in YAML containing the needed
[bot properties](https://code.google.com/p/aiml-en-us-foundation-alice/wiki/BotProperties)

After that, just run `cardboardbot.py` and it should automatically create the
brain file and connect to the server, joining the chatroom you defined in
`config.py`

If you want a nifty webapp to display logs and statistics, take a look at
[CardboardLog](http://github.com/woll0r/cardboardlog)
