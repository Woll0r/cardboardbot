#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""CardboardBot module that handles general chatbot things"""

import logging
import sys

import sleekxmpp  # Jabber library

from .CardboardAlice import CardboardAlice
from .CardboardCommands import CardboardCommands
from .CardboardDummyBrain import CardboardDummyBrain
from .CardboardIq import CardboardIq
from .CardboardLinks import CardboardLinks
from .CardboardLookup import CardboardLookup
from .CardboardMessageHandler import CardboardMessageHandler
from .CardboardPresenceHandler import CardboardPresenceHandler
from .CardboardSqlite import CardboardDatabase

# Python versions before 3.0 do not use UTF-8 encoding
# by default.  To ensure that Unicode is handled properly
# throughout SleekXMPP, we will set the default encoding
# ourselves to UTF-8.
if sys.version_info < (3, 0):
    from sleekxmpp.util.misc_ops import setdefaultencoding
    setdefaultencoding('utf8')

log = logging.getLogger(__name__)


class CardboardBot(sleekxmpp.ClientXMPP):
    """CardboardBot class that will handle
    all client-side XMPP things for the bot"""

    # Class constructor
    def __init__(self, jid, password, nick, channel, use_ipv6,
                 brainfile, memoriesfile, aimlpath, databasefile):
        # Set parameters for SleekXMPP
        log.debug("Initiating CardboardBot by setting my own parameters...")
        super(CardboardBot, self).__init__(jid, password)

        self.nick = nick
        self.jid = jid
        self.channel = channel

        # This is public because for some reason
        # SleekXMPP requires it to be that way
        self.use_ipv6 = use_ipv6

        # Tell SleekXMPP to use message IDs to prevent certain broken-ness in
        # how Xabber deals with messages
        self.use_message_ids = True

        # Setup AI handler
        if sys.version_info < (3, 0):
            self._brain = CardboardAlice(brainfile=brainfile,
                                         memoriesfile=memoriesfile,
                                         aimlpath=aimlpath, nick=self.nick)
        else:
            log.warning("No aiml module on Python3, not using Alice")
            self._brain = CardboardDummyBrain()

        # Setup other handlers
        self._db = CardboardDatabase(databasefile=databasefile)
        self._links = CardboardLinks(database=self._db)
        self._lookup = CardboardLookup(links=self._links)
        self._iq = CardboardIq(connection=self)
        self._commands = CardboardCommands(database=self._db, connection=self, iq=self._iq)
        self._messagehandler = CardboardMessageHandler(brain=self._brain,
                                                       cmd=self._commands,
                                                       database=self._db,
                                                       links=self._links,
                                                       nickname=self.nick,
                                                       lookup=self._lookup,
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

    def create_iq(self, id, itype, payload, namespace):
        """Create the XMPP IQ xml payload for an action"""
        iq = self.make_iq(id=id, ifrom=self.jid, ito=self.channel,
                          itype=itype)
        iq.set_query(namespace)
        iq.set_payload(payload)
        return iq
