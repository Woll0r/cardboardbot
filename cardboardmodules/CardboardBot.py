#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""CardboardBot module that handles general chatbot things"""

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
    """CardboardBot class that will handle all client-side XMPP things for the bot"""
    # pylint: disable=too-many-instance-attributes

    # Class constructor
    def __init__(self, jid, password, nick, channel, use_ipv6,
                 brainfile, memoriesfile, aimlpath, databasefile):
        # pylint: disable=too-many-arguments
        # Set parameters for SleekXMPP
        log.debug("Initiating CardboardBot by setting my own parameters...")
        super(CardboardBot, self).__init__(jid, password)

        self.nick = nick
        self.channel = channel

        # This is public because for some reason SleekXMPP requires it to be that way
        self.use_ipv6 = use_ipv6

        # Setup AI handler
        if sys.version_info < (3, 0):
            self._brain = CardboardAlice(brainfile=brainfile, memoriesfile=memoriesfile,
                                         aimlpath=aimlpath, nick=self.nick)
        else:
            log.warning("Alice requires the aiml module which isn't available on Python 3!")
            self._brain = CardboardDummyBrain()

        # Setup other handlers
        self._db = CardboardDatabase(databasefile=databasefile)
        self._commands = CardboardCommands(database=self._db, connection=self)
        self._links = CardboardLinks(database=self._db)
        self._lookup = CardboardLookup(links=self._links)
        self._messagehandler = CardboardMessageHandler(brain=self._brain, cmd=self._commands,
                                                       database=self._db, links=self._links,
                                                       nickname=self.nick, lookup=self._lookup,
                                                       connection=self)
        self._presencehandler = CardboardPresenceHandler(database=self._db)

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
        """Bot startup event handler"""
        # pylint: disable=unused-argument
        log.debug("Connection established, saying hello to the server")
        self.send_presence()
        self.get_roster()
        self.plugin['xep_0045'].joinMUC(self.channel, self.nick, wait=False)

    def groupchatmessage(self, event):
        """Bot groupchat message event handler"""
        log.debug("I got a message! Sending to handler!")
        self._messagehandler.handler(event)

    def groupchatpresence(self, event):
        """Bot groupchat presence event handler"""
        log.debug("I got a presence! Sending to handler!")
        self._presencehandler.handler(event)
