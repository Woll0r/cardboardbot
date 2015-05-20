#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

# Python versions before 3.0 do not use UTF-8 encoding
# by default.  To ensure that Unicode is handled properly
# throughout SleekXMPP, we will set the default encoding
# ourselves to UTF-8.
if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')
else:
    raw_input = input

import logging

import sleekxmpp  # Jabber library
from .CardboardAlice import CardboardAlice
from .CardboardCommands import CardboardCommands
from .CardboardSqlite import CardboardDatabase
from .CardboardMessageHandler import CardboardMessageHandler
from .CardboardLinks import CardboardLinks
from .CardboardLookup import CardboardLookup
from .CardboardPresenceHandler import CardboardPresenceHandler
from .CardboardDummyBrain import CardboardDummyBrain

log = logging.getLogger(__name__)


class CardboardBot(sleekxmpp.ClientXMPP):
    # Class constructor
    def __init__(self, jid, password, nick, channel, use_ipv6, braintype, brainfile, memoriesfile, aimlpath, databasefile):
        # Set parameters for SleekXMPP
        log.debug("Initiating CardboardBot by setting my own parameters...")
        super(CardboardBot, self).__init__(jid, password)

        # Configure my own parameters
        self.jid = jid
        self.password = password
        self.nick = nick
        self.channel = channel

        if not use_ipv6:
            self.use_ipv6 = False

        # Setup AI handler
        if sys.version_info < (3, 0):
            self.ai = CardboardAlice(brainfile=brainfile, memoriesfile=memoriesfile, aimlpath=aimlpath, nick=self.nick)
        else:
            log.warning("Alice requires the aiml module which isn't available on Python 3!")
            self.ai = CardboardDummyBrain()

        # Setup other handlers
        self.db = CardboardDatabase(databasefile=databasefile)
        self.commands = CardboardCommands(db=self.db, connection=self)
        self.links = CardboardLinks(db=self.db)
        self.lookup = CardboardLookup(db=self.db, links=self.links)
        self.messagehandler = CardboardMessageHandler(ai=self.ai, cmd=self.commands, db=self.db, links=self.links, nickname=self.nick,
                                        lookup=self.lookup, connection=self)
        self.presencehandler = CardboardPresenceHandler(db=self.db)

        self.register_plugin('xep_0030')  # Service Discovery
        self.register_plugin('xep_0004')  # Data Forms
        self.register_plugin('xep_0045')  # Jabber MUC
        self.register_plugin('xep_0060')  # PubSub
        self.register_plugin('xep_0199')  # XMPP Ping

        # Add event handling for Jabber events
        log.debug("Initialize event handlers...")
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("groupchat_message", self.groupchatmessage)
        self.add_event_handler("groupchat_presence", self.groupchatpresence)

    # Handle the start event (connection to Jabber)
    def start(self, event):
        log.debug("Connection established, saying hello to the server")
        self.send_presence()
        self.get_roster()
        self.plugin['xep_0045'].joinMUC(self.channel, self.nick, wait=False)

    def groupchatmessage(self, event):
        log.debug("I got a message! Sending to handler!")
        self.messagehandler.handler(event)

    def groupchatpresence(self, event):
        log.debug("I got a presence! Sending to handler!")
        self.presencehandler.handler(event)