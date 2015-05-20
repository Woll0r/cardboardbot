#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""CardboardMessageHandler module for handling incoming messages"""

import logging
import time

from cardboardmodules.CardboardMessage import CardboardMessage, Message


log = logging.getLogger(__name__)


class CardboardMessageHandler(object):
    """CardboardMessageHandler class for handling incoming messages"""
    # pylint: disable=too-few-public-methods

    def __init__(self, brain, cmd, database, links, nickname, lookup, connection):
        # pylint: disable=too-many-arguments
        log.debug("CardboardPresenceHandler init")
        self._brain = brain
        self._cmd = cmd
        self._db = database
        self._links = links
        self._nick = nickname
        self._lookup = lookup
        self._connection = connection

    def handler(self, msg):
        """Handle incoming messages"""
        # pylint: disable=too-many-return-statements,too-many-branches,too-many-statements
        log.debug("handler received message")

        # Don't respond to empty messages
        if not msg["body"]:
            return

        # Don't respond to the MOTD
        if msg["subject"]:
            return

        messager = CardboardMessage(connection=self._connection,
                                    default_destination=msg["from"].bare)

        timestamp = int(time.time())
        userjid = self._cmd.get_user_jid(msg["mucnick"])

        messageobject = Message(msg["body"], sendernick=msg['mucnick'], sender=userjid.bare,
                                html=msg["html"] or None, destination=msg["from"].bare,
                                nick=self._connection.nick)

        log.info("%s: %s", messageobject.sendernick, messageobject.plain)

        # Log messages in the database
        if userjid is not None:
            self._db.insert_in_messages_table(timestamp, messageobject.sendernick,
                                              userjid.bare, messageobject.plain)

        # Don't respond to ourself
        if messageobject.sendernick == self._nick:
            return

        # Handle links in messages
        urls = self._links.handle_url(timestamp, userjid.bare, messageobject.plain)
        if urls:
            message = messager.create_message(urls)
            messager.send_message(message)

        # Respond to mentions
        # if connection.nick.lower() in messagebody.lower():
        if messageobject.is_ping:
            log.debug("Someone said my name!")

            # Administrative commands
            if messageobject.command == "kick":
                log.debug("Kick command detected")
                #to_kick = messagebody.split("!kick ")[-1]
                result = self._cmd.kick_user(messageobject.args, messageobject.sendernick)
                message = messager.create_message(result)
                messager.send_message(message)
                return

            if messageobject.command == "identify":
                log.debug("Identify command detected")
                #to_identify = messagebody.split("!identify ")[-1]
                affiliation = self._cmd.get_user_affiliation(messageobject.args)
                role = self._cmd.get_user_role(messageobject.args)
                jid = self._cmd.get_user_jid(messageobject.args)
                if affiliation:
                    message = messager.create_message("%s was identified as %s, "\
                        "with role %s and affiliation %s" %
                                                      (messageobject.args, jid.bare,
                                                       role, affiliation))
                else:
                    message = messager.create_message("%s is not in the room!" %
                                                      (messageobject.args, ))
                messager.send_message(message)
                return

            # sudo
            if messageobject.command == "sudo":
                log.debug("Someone wants to use sudo!")
                message = messager.create_message(self._cmd.sudo(messageobject))
                messager.send_message(message)
                return

            # ping!
            if messageobject.command == "ping":
                log.debug("Someone wants to send a ping!")
                message = messager.create_message(plaintext=messageobject.stripped,
                                                  destination='sweetiebutt@'\
                                                      'friendshipismagicsquad.com')
                messager.send_message(message, mtype='chat')

                return

            # Last seen
            if messageobject.command == "seen":
                log.debug("Someone wants to know when a person was last online!")
                message = messager.create_message(self._cmd.seen(messageobject.args))
                messager.send_message(message)
                return

            # Last said
            if messageobject.command == "lastsaid":
                log.debug("Someone wants to know when a person last spoke!")
                message = messager.create_message(self._cmd.lastsaid(messageobject.args))
                messager.send_message(message)
                return

            # Tumblr argueing
            if messageobject.command == "argue":
                log.debug("Someone wants me to argue!")
                message = messager.create_message(self._cmd.argue())
                messager.send_message(message)
                return

            # Tumblr rant
            if messageobject.command == "rant":
                log.debug("Someone wants me to rant!")
                message = messager.create_message(self._cmd.rant())
                messager.send_message(message)
                return

            # Diceroll
            if messageobject.command == "roll":
                log.debug("Someone asked for a diceroll!")
                message = messager.create_message(self._cmd.roll(messageobject.args))
                messager.send_message(message)
                return

            # Pony
            if messageobject.command == "pony":
                log.debug("Someone asked for ponies!")
                plain, html = self._lookup.pony(messageobject.sendernick, timestamp)
                message = messager.create_message(plaintext=plain, html=html)
                messager.send_message(message)
                return

            # clop
            if messageobject.command == "clop":
                log.debug("Someone asked for clop!")
                plain, html = self._lookup.clop(messageobject.sendernick, timestamp)
                message = messager.create_message(plaintext=plain, html=html)
                messager.send_message(message)
                return

            # ferret
            if messageobject.command == "ferret":
                log.debug("Someone asked for ferrets!")
                plain, html = self._lookup.ferret(messageobject.sendernick, timestamp)
                message = messager.create_message(plaintext=plain, html=html)
                messager.send_message(message)
                return

            # subreddit
            if messageobject.command == "redditlookup":
                plain, html = self._lookup.lookup(messageobject.args, messageobject.sendernick,
                                                  timestamp)
                message = messager.create_message(plaintext=plain, html=html)
                messager.send_message(message)
                return


            # deowl
            if messageobject.command == "deowl":
                result = self._cmd.kick_user("owlowiscious", messageobject.sendernick)
                message = messager.create_message(result)
                messager.send_message(message)
                return

            # deflower
            if messageobject.command == "deflower":
                if self._cmd.get_user_affiliation("roseluck") is not None:
                    result = self._cmd.kick_user("roseluck", messageobject.sendernick)
                else:
                    result = self._cmd.kick_user("Roseluck", messageobject.sendernick)
                message = messager.create_message(result)
                messager.send_message(message)
                return

            # Someone does things to me!
            if messageobject.is_action:
                log.debug("I am being touched by %s!", messageobject.sendernick)
                message = messager.create_message(self._cmd.tuch(messageobject.sendernick,
                                                                 messageobject.plain))
                messager.send_message(message)
                return

            # C/D mode
            if messageobject.plain.lower().endswith("c/d") or \
                messageobject.plain.lower().endswith("c/d?"):
                #if messagebody.lower().endswith("c/d") or messagebody.lower().endswith("c/d?"):
                log.debug("Confirm/deny detected")
                message = messager.create_message("%s: %s" % (messageobject.sendernick,
                                                              self._cmd.ceedee()))
                messager.send_message(message)
                return

            # Delegate response to Alice
            log.debug("I don't know what to say, delegating to Alice")
            message = messager.create_message(self._brain.response(messageobject.sendernick,
                                                                   messageobject.plain))
            messager.send_message(message)
            return

        return
