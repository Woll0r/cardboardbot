#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import cgi

log = logging.getLogger(__name__)


def to_html(plain):
    html = cgi.escape(plain).replace('\n', '<br />')
    return html


class Message:
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
        self.stripped = self.strip_nick(nick, plain)

        self.command, self.args = self.command_and_args(self.stripped)


    def command_and_args(self, stripped):
        if ' ' in stripped:
            command, args = [x.strip() for x in stripped.split(None, 1)]
        else:
            command, args = stripped, ''

        return command, args

    def msg_is_command(self, nick, plain):
        return plain.lower().strip().startswith(nick.lower)

    def msg_is_ping(self, nick, plain):
        return nick.lower() in plain.lower()

    def strip_nick(self, nick, plain):
        plain = plain.strip()
        if plain.lower().startswith(nick.lower()):
            plain = plain[len(nick):]
        plain = plain.strip()
        if plain.startswith(':') or plain.startswith(','):
            plain = plain[1:]
        return plain.strip()


class CardboardMessage:
    def __init__(self, connection, default_destination):
        log.debug("CardboardMessage init")
        self.connection = connection
        self.default_destination = default_destination

    def create_message(self, plaintext=None, html=None, destination=None):
        log.debug("Creating message: %s, %s, %s" % (plaintext, html, destination))
        if destination is None:
            destination = self.default_destination
        message = Message(plain=plaintext, html=html, destination=destination)
        return message

    def send_message(self, message=None, type="groupchat"):
        log.debug("Sending message: %s" % message.plain)
        log.debug("Destination: %s, type: %s" % (message.destination, type))
        self.connection.send_message(mto=message.destination,
                                     mbody=message.plain,
                                     mhtml=message.html,
                                     mtype=type)