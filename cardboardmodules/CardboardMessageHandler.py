#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import time

from cardboardmodules.CardboardMessage import CardboardMessage, Message


log = logging.getLogger(__name__)


class CardboardMessageHandler:
    def __init__(self, ai, cmd, db, links, nickname, lookup, connection):
        log.debug("CardboardPresenceHandler init")
        self.ai = ai
        self.cmd = cmd
        self.db = db
        self.links = links
        self.nick = nickname
        self.lookup = lookup
        self.connection = connection

    def handler(self, msg):
        log.debug("handler received message")
        """Handle incoming messages"""

        # Don't respond to empty messages
        if not msg["body"]:
            return

        # Don't respond to the MOTD
        if msg["subject"]:
            return

        messager = CardboardMessage(connection=self.connection, default_destination=msg["from"].bare)

        timestamp = int(time.time())
        sender = msg["mucnick"]
        userjid = self.cmd.get_user_jid(sender)
        messagebody = msg["body"]

        messageobject = Message(msg["body"], sendernick=msg['mucnick'], sender=userjid.bare, html=msg["html"] or None,
                                destination=msg["from"].bare, nick=self.connection.nick)

        fullmessage = sender + ": " + messagebody
        log.info(fullmessage)

        # Log messages in the database
        if userjid is not None:
            self.db.insert_in_messages_table(timestamp, sender, userjid.bare, messagebody)

        # Don't respond to ourself
        if sender == self.nick:
            return

        # Handle links in messages
        urls = self.links.handle_url(timestamp, userjid.bare, messagebody)
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
                to_kick = messageobject.args
                result = self.cmd.kick_user(to_kick, sender)
                message = messager.create_message(result)
                messager.send_message(message)
                return

            if messageobject.command == "identify":
                log.debug("Identify command detected")
                #to_identify = messagebody.split("!identify ")[-1]
                to_identify = messageobject.args
                affiliation = self.cmd.get_user_affiliation(to_identify)
                role = self.cmd.get_user_role(to_identify)
                userjid = self.cmd.get_user_jid(to_identify)
                if affiliation:
                    message = messager.create_message("%s was identified as %s, with role %s and affiliation %s" % (
                        to_identify, userjid.bare, role, affiliation))
                else:
                    message = messager.create_message("%s is not in the room!" % (to_identify, ))
                messager.send_message(message)
                return

            # ping!
            if messageobject.command == "ping":
                log.debug("Someone wants to send a ping!")
                ping = messagebody.replace(self.nick + ": ", "", 1)

                message = messager.create_message(plaintext=ping, destination='sweetiebutt@friendshipismagicsquad.com')
                messager.send_message(message, type='chat')

                return

            # Last seen
            if messageobject.command == "seen":
                log.debug("Someone wants to know when a person was last online!")
                requested_nick = messageobject.args
                message = messager.create_message(self.cmd.seen(requested_nick))
                messager.send_message(message)
                return

            # Last said
            if messageobject.command == "lastsaid":
                log.debug("Someone wants to know when a person last spoke!")
                requested_nick = messageobject.args
                message = messager.create_message(self.cmd.lastsaid(requested_nick))
                messager.send_message(message)
                return

            # Tumblr argueing
            if messageobject.command == "argue":
                log.debug("Someone wants me to argue!")
                message = messager.create_message(self.cmd.argue())
                messager.send_message(message)
                return

            # Tumblr rant
            if messageobject.command == "rant":
                log.debug("Someone wants me to rant!")
                message = messager.create_message(self.cmd.rant())
                messager.send_message(message)
                return

            # Diceroll
            if messageobject.command == "roll":
                #if "roll" in messagebody.lower():
                log.debug("Someone asked for a diceroll!")
                #dice = messagebody.lower().split("roll ")[-1]
                dice = messageobject.args
                message = messager.create_message(self.cmd.roll(dice))
                messager.send_message(message)
                return

            # Pony
            if messageobject.command == "pony":
                log.debug("Someone asked for ponies!")
                plain, html = self.lookup.pony(sender, timestamp)
                message = messager.create_message(plaintext=plain, html=html)
                messager.send_message(message)
                return

            # clop
            if messageobject.command == "clop":
                log.debug("Someone asked for clop!")
                plain, html = self.lookup.clop(sender, timestamp)
                message = messager.create_message(plaintext=plain, html=html)
                messager.send_message(message)
                return

            # ferret
            if messageobject.command == "ferret":
                log.debug("Someone asked for ferrets!")
                plain, html = self.lookup.ferret(sender, timestamp)
                message = messager.create_message(plaintext=plain, html=html)
                messager.send_message(message)
                return

            # subreddit
            if messageobject.command == "redditlookup":
                #subreddit = messagebody.lower().split("redditlookup ")[-1]
                subreddit = messageobject.args
                plain, html = self.lookup.lookup(subreddit, sender, timestamp)
                message = messager.create_message(plaintext=plain, html=html)
                messager.send_message(message)
                return


            # deowl
            if messageobject.command == "deowl":
                result = self.cmd.kick_user("owlowiscious", sender)
                message = messager.create_message(result)
                messager.send_message(message)
                return

            # deflower
            if messageobject.command == "deflower":
                if self.cmd.get_user_affiliation("roseluck") is not None:
                    result = self.cmd.kick_user("roseluck", sender)
                else:
                    result = self.cmd.kick_user("Roseluck", sender)
                message = messager.create_message(result)
                messager.send_message(message)
                return

            # Someone does things to me!
            if messageobject.is_action:
                log.debug("I am being touched by %s!" % sender)
                message = messager.create_message(self.cmd.tuch(sender, messagebody))
                messager.send_message(message)
                return

            # C/D mode
            if messageobject.plain.lower().endswith("c/d") or messageobject.plain.lower().endswith("c/d?"):
                #if messagebody.lower().endswith("c/d") or messagebody.lower().endswith("c/d?"):
                log.debug("Confirm/deny detected")
                message = messager.create_message("%s: %s" % (sender, self.cmd.ceedee()))
                messager.send_message(message)
                return

            # Delegate response to Alice
            log.debug("I don't know what to say, delegating to Alice")
            message = messager.create_message(self.ai.response(sender, messagebody))
            messager.send_message(message)
            return

        return
