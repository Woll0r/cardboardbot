#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Python versions before 3.0 do not use UTF-8 encoding
# by default. To ensure that Unicode is handled properly
# throughout SleekXMPP, we will set the default encoding
# ourselves to UTF-8.
if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')
else:
    raw_input = input

import logging

import sleekxmpp                   # Jabber library
import ssl                         # SSL connections to Jabbers!

from CardboardBrain import CardboardBrain
from CardboardCommands import CardboardCommands
from CardboardDatabase import CardboardDatabase
from CardboardHandler import CardboardHandler
from CardboardLinks import CardboardLinks

log = logging.getLogger(__name__)

class CardboardBot(sleekxmpp.ClientXMPP):
    # Class constructor
    def __init__(self, config):
        # Set parameters for SleekXMPP
        log.debug("Initiating CardboardBot by setting my own parameters...")
        super(CardboardBot, self).__init__(config.jid, config.password)

        # Configure my own parameters
        self.jid = config.jid
        self.password = config.password
        self.nick = config.nick
        self.channel = config.channel
        
        if not config.useipv6:
            self.use_ipv6 = False

        # Setup handlers
        self.ai = CardboardBrain(config.brainfile, config.memoriesfile, config.aimlpath)
        self.db = CardboardDatabase(config.databasefile)
        self.commands = CardboardCommands(self.db)
        self.links = CardboardLinks(self.db)
        self.handler = CardboardHandler(self.ai, self.cmd, self.db, self.links, self.nick)
              
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
        self.handler.handler(self, event)