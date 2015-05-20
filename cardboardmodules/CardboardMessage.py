#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""CardboardMessage module for creating and handling messages"""

import logging
import cgi

log = logging.getLogger(__name__)


def to_html(plain):
    """Create a HTML-formatted message out of a plaintext message"""
    html = cgi.escape(plain).replace('\n', '<br />')
    return html


class Message(object):
    """Message class for having a single object containing messages"""
    # pylint: disable=too-many-instance-attributes,too-many-arguments,no-self-use

    def __init__(self, plain, destination, html=None, sender=None, sendernick=None, nick=None):
        log.debug("Message init")
        self.plain = plain
        self.html = html or to_html(plain)
        self.destination = destination
        self.sender = sender
        self.sendernick = sendernick
        self.nick = nick
        self.is_ping = self.msg_is_ping(nick, plain)
        self.is_command = self.msg_is_command(nick, plain)
        self.is_action = self.msg_is_action(plain)
        self.stripped = self.strip_nick(nick, plain)
        self.command, self.args = self.command_and_args(self.stripped)

    def command_and_args(self, stripped):
        """Get the command and arguments out of a message sent to the bot"""
        if ' ' in stripped:
            command, args = [x.strip() for x in stripped.split(None, 1)]
        else:
            command, args = stripped, ''

        command = command.lower()
        #args = args.lower()

        return command, args

    def msg_is_action(self, plain):
        """See if the message is an emote action"""
        if plain is None:
            return False
        if plain.startswith("/me"):
            return True
        return False

    def msg_is_command(self, nick, plain):
        """See if the message is a bot command"""
        if nick is None:
            return False
        if plain is None:
            return False
        return plain.lower().strip().startswith(nick.lower())

    def msg_is_ping(self, nick, plain):
        """See if the message is pinged to the bot"""
        if nick is None:
            return False
        if plain is None:
            return False
        return nick.lower() in plain.lower()

    def strip_nick(self, nick, plain):
        """Strip the bot's own nick from the message"""
        if nick is None:
            return plain.strip()
        plain = plain.strip()
        if plain.lower().startswith(nick.lower()):
            plain = plain[len(nick):]
        plain = plain.strip()
        if plain.startswith(':') or plain.startswith(','):
            plain = plain[1:]
        return plain.strip()


class CardboardMessage(object):
    """CardboardMessage class for creating and sending messages"""
    def __init__(self, connection, default_destination):
        log.debug("CardboardMessage init")
        self.connection = connection
        self.default_destination = default_destination

    def create_message(self, plaintext=None, html=None, destination=None):
        """Create a message with the given parameters"""
        log.debug("Creating message: %s, %s, %s", plaintext, html, destination)
        if destination is None:
            destination = self.default_destination
        message = Message(plain=plaintext, html=html, destination=destination)
        return message

    def send_message(self, message=None, mtype="groupchat"):
        """Send a message to the recipient"""
        log.debug("Sending message: %s", message.plain)
        log.debug("Destination: %s, type: %s", message.destination, mtype)
        self.connection.send_message(mto=message.destination,
                                     mbody=message.plain,
                                     mhtml=message.html,
                                     mtype=mtype)
