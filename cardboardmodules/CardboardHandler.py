#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import time
from cardboardmodules.CardboardMessage import CardboardMessage

log = logging.getLogger(__name__)


class CardboardHandler:
    def __init__(self, ai, cmd, db, links, nickname, lookup):
        self.ai = ai
        self.cmd = cmd
        self.db = db
        self.links = links
        self.nick = nickname
        self.lookup = lookup

    def handler(self, connection, msg):
        """Handle incoming messages"""

        messager = CardboardMessage(connection=connection, default_destination=msg["from"].bare)

        timestamp = int(time.time())
        sender = msg["mucnick"]
        userjid = self.cmd.get_user_jid(connection, sender)
        messagebody = msg["body"]

        fullmessage = sender + ": " + messagebody
        log.info(fullmessage)

        # Log messages in the database
        if userjid is not None:
            self.db.insert_in_messages_table(timestamp, sender, userjid.bare, messagebody)

        # Don't respond to the MOTD
        if not len(sender):
            return

        # Don't respond to ourself
        if sender == self.nick:
            return

        # Handle links in messages
        urls = self.links.handle_url(timestamp, userjid.bare, messagebody)
        if urls:
            message = messager.create_message(urls)
            messager.send_message(message)

        # Administrative commands
        if "!kick" in messagebody.lower():
            log.debug("Kick command detected")
            to_kick = messagebody.split("!kick ")[-1]
            result = self.cmd.kick_user(connection, to_kick, sender, msg["from"].bare)
            message = messager.create_message(result)
            messager.send_message(message)
            return

        if "!identify" in messagebody.lower():
            log.debug("Identify command detected")
            to_identify = messagebody.split("!identify ")[-1]
            affiliation = self.cmd.get_user_affiliation(connection, to_identify)
            role = self.cmd.get_user_role(connection, to_identify)
            userjid = self.cmd.get_user_jid(connection, to_identify)

            message = messager.create_message("%s was identified as %s, with role %s and affiliation %s" % (to_identify, userjid.bare, role, affiliation))
            messager.send_message(message)
            return

        # Respond to mentions
        if connection.nick.lower() in messagebody.lower():
            log.debug("Someone said my name!")

            # ping!
            if "ping" in messagebody.lower():
                log.debug("Someone wants to send a ping!")
                ping = messagebody.replace(self.nick + ": ", "", 1)

                message = messager.create_message(plaintext=ping, destination='sweetiebutt@friendshipismagicsquad.com')
                messager.send_message(message, type='chat')

                return

            # C/D mode
            if messagebody.lower().endswith("c/d") or messagebody.lower().endswith("c/d?"):
                log.debug("Confirm/deny detected")
                message = messager.create_message("%s: %s" % (sender, self.cmd.ceedee()))
                messager.send_message(message)
                return

            # Someone does things to me!
            if messagebody.lower().startswith("/me"):
                log.debug("I am being touched by %s!" % sender)
                message = messager.create_message(self.cmd.tuch(sender, messagebody))
                messager.send_message(message)
                return

            # Tumblr argueing
            if "argue" in messagebody.lower():
                log.debug("Someone wants me to argue!")
                message = messager.create_message(self.cmd.argue())
                messager.send_message(message)
                return

            # Tumblr rant
            if "rant" in messagebody.lower():
                log.debug("Someone wants me to rant!")
                message = messager.create_message(self.cmd.rant())
                messager.send_message(message)
                return

            # Diceroll
            if "roll" in messagebody.lower():
                log.debug("Someone asked for a diceroll!")
                dice = messagebody.lower().split("roll ")[-1]
                message = messager.create_message(self.cmd.roll(dice))
                messager.send_message(message)
                return

            # Pony
            if "pony" in messagebody.lower():
                log.debug("Someone asked for ponies!")
                url, title = self.lookup.pony(sender, timestamp)
                html = '<a href="{}">{}</a>'.format(url, title)
                plain = '{} [{}]'.format(title, url)
                message = messager.create_message(plaintext=plain, html=html)
                messager.send_message(message)

            # clop
            if "clop" in messagebody.lower():
                log.debug("Someone asked for clop!")
                url, title = self.lookup.pony(sender, timestamp)
                html = ':nws: <a href="{}">{}</a> :nws:'.format(url, title)
                plain = '{} [{}]'.format(title, url)
                message = messager.create_message(plaintext=plain, html=html)
                messager.send_message(message)

            # Delegate response to Alice
            log.debug("I don't know what to say, delegating to Alice")
            message = messager.create_message(self.ai.alicemessage(sender, messagebody))
            messager.send_message(message)
            return

        return