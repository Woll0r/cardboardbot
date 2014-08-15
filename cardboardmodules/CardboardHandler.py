#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

# Needed for logging
import time

log = logging.getLogger(__name__)

class CardboardHandler:

    def __init__(self, ai, cmd, db, links, nickname):
        self.ai = ai
        self.cmd = cmd
        self.db = db
        self.links = links
        self.nick = nickname
        
    def handler(self, connection, msg):
        """Handle incoming messages"""

        timestamp = int(time.time())
        sender = msg["mucnick"]
        userjid = self.cmd.get_user_jid(connection, sender)
        message = msg["body"]
        
        fullmessage = sender + ": " + message
        log.info(fullmessage)
    
        # Log messages in the database
        if userjid is not None:
            self.db.insert_in_messages_table(timestamp, sender, userjid.bare, message)

        # Don't respond to the MOTD
        if not len(sender):
            return
    
        # Don't respond to ourself
        if sender == self.nick:
            return

        # Handle links in messages
        urls = self.links.handle_url(timestamp, userjid.bare, message)
        if urls:
            connection.send_message(mto=msg["from"].bare,
                    mbody=urls,
                    mtype="groupchat")
        
        # Administrative commands
        if "!kick" in message.lower():
            log.debug("Kick command detected")
            to_kick = message.split("!kick ")[-1]
            self.cmd.kick_user(connection, to_kick, sender, msg["from"].bare)
            return

        if "!identify" in message.lower():
            log.debug("Identify command detected")
            to_identify = message.split("!identify ")[-1]
            affiliation = self.cmd.get_user_affiliation(connection, to_identify)
            role = self.cmd.get_user_role(connection, to_identify)
            userjid = self.cmd.get_user_jid(connection, to_identify)
            connection.send_message(mto=msg["from"].bare,
                    mbody="%s was identified as %s, with role %s and affiliation %s" %(to_identify, userjid.bare, role, affiliation),
                    mtype="groupchat")
            return
        
        # Respond to mentions
        if connection.nick.lower() in message.lower():
            log.debug("Someone said my name!")
        
            # ping!
            if "ping" in message.lower():
                log.debug("Someone wants to send a ping!")
                ping = message.replace(self.nick + ": ", "", 1)
                connection.send_message(mto="sweetiebutt@friendshipismagicsquad.com",
                    mbody=ping,
                    mtype="chat")
                return
            
            # C/D mode
            if message.lower().endswith("c/d") or message.lower().endswith("c/d?"):
                log.debug("Confirm/deny detected")
                connection.send_message(mto=msg["from"].bare,
                    mbody="%s: %s" %(sender, self.cmd.ceedee()),
                    mtype="groupchat")
                return
        
            # Someone does things to me!
            if message.lower().startswith("/me"):
                log.debug("I am being touched by %s!" % sender)
                connection.send_message(mto=msg["from"].bare,
                        mbody=self.cmd.tuch(sender, message),
                        mtype="groupchat")
                return
        
            # Tumblr argueing
            if "argue" in message.lower():
                log.debug("Someone wants me to argue!")
                connection.send_message(mto=msg["from"].bare,
                        mbody=self.cmd.argue(),
                        mtype="groupchat")
                return

            # Tumblr rant
            if "rant" in message.lower():
                log.debug("Someone wants me to rant!")
                connection.send_message(mto=msg["from"].bare,
                        mbody=self.cmd.rant(),
                        mtype="groupchat")
                return

            # Diceroll
            if "roll" in message.lower():
                log.debug("Someone asked for a diceroll!")
                
            # Delegate response to Alice
            log.debug("I don't know what to say, delegating to Alice")
            dice = message.split("roll ")[-1]
            connection.send_message(mto=msg["from"].bare,
                    mbody=self.cmd.roll(dice),
                    mtype="groupchat")
            return
        
        return