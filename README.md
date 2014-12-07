# Cardboardbot

A Jabber chatbot with a bunch of uses

## Requirements

Requires Python 2.7 and will not run with Python 3 because some of the modules
used don't work with Python 3.

You can install the required Python packages with a simple
`pip install -r requirements.txt`

You will also need an AIML library for the bot to use. I personally used the
[A.L.I.C.E. AIML set](https://code.google.com/p/aiml-en-us-foundation-alice/)
which works nicely.

## Usage

Create your own `config.py` based on the example provided. Give your bot some
personality by creating a personality file in YAML containing the needed
[bot properties](https://code.google.com/p/aiml-en-us-foundation-alice/wiki/BotProperties)

After that, just run `cardboardbot.py` and it should automatically create the
brain file and connect to the server, joining the chatroom you defined in
`config.py`

If you want a nifty webapp to display logs and statistics, take a look at
[CardboardLog](http://github.com/woll0r/cardboardlog)
