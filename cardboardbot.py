#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys                         # Systems stuff
import logging                     # Logging
from optparse import OptionParser  # Parse commandline options
import sleekxmpp                   # Jabber library
import ssl                         # SSL connections to Jabbers!

# Try to get the configuration file and other external files
import config
import botcommands

# Python versions before 3.0 do not use UTF-8 encoding
# by default. To ensure that Unicode is handled properly
# throughout SleekXMPP, we will set the default encoding
# ourselves to UTF-8.
if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')
else:
    raw_input = input

log = logging.getLogger(__name__)
    
class CardboardBot(sleekxmpp.ClientXMPP):
    # Class constructor
    def __init__(self, jid, password, nick, channel):
        # Set parameters for SleekXMPP
        log.debug("Initiating CardboardBot by setting my own parameters...")
        super(CardboardBot, self).__init__(jid, password)

        # Configure my own parameters
        self.jid = jid
        self.password = password
        self.nick = nick
        self.channel = channel

        # Disable IPv6 lookups for speed
        self.use_ipv6 = False

        log.debug("Start up my brain...")
        botcommands.brain_start()

        # Add event handling for Jabber events
        log.debug("Initialize event handlers...")
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("groupchat_message", self.groupchatmessage)
        
        self.register_plugin('xep_0030') # Service Discovery
        self.register_plugin('xep_0004') # Data Forms
        self.register_plugin('xep_0045') # Jabber MUC
        self.register_plugin('xep_0060') # PubSub
        self.register_plugin('xep_0199') # XMPP Ping

    # Handle the start event (connection to Jabber)
    def start(self, event):
        log.debug("Connection established, saying hello to the server")
        self.send_presence()
        self.get_roster()
        self.plugin['xep_0045'].joinMUC(self.channel, self.nick, wait=False)

    def groupchatmessage(self, event):
        log.debug("I got a message! Sending to handler!")
        botcommands.handler(self, event)

if __name__ == '__main__':
    # Setup the command line arguments.
    optp = OptionParser()

    # JID and password options.
    optp.add_option("-j", "--jid", dest="jid",
                    help="JID to use")
    optp.add_option("-p", "--password", dest="password",
                    help="password to use")
    optp.add_option("-n", "--nick", dest="nick",
                    help="Nick to use in channels.")
    optp.add_option("-c", "--channel", dest="channel",
                    help="Channel to work in.")

    opts, args = optp.parse_args()

    # Setup logging.
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(name)s %(message)s',
                        filename='cardboardbot.log',
                        filemode='w+')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)-8s %(name)s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    if opts.jid is None:
        try:
            opts.jid = config.jid
        except NameError:
            log.critical("I require a JID!")
            exit(1)
    if opts.password is None:
        try:
            opts.password = config.password
        except NameError:
            log.critical("I require a password!")
            exit(1)
    if opts.nick is None:
        try:
            opts.nick = config.nick
        except NameError:
            log.critical("I require a nick!")
            exit(1)
    if opts.channel is None:
        try:
            opts.channel = config.channel
        except NameError:
            log.critical("I require a channel!")
            exit(1)

    # Set up the bot and it's required XMPP things
    xmpp = CardboardBot(opts.jid, opts.password, opts.nick, opts.channel)

    # Connect!
    if xmpp.connect():
        xmpp.process(block=True)
    else:
        log.critical("Unable to connect!")
