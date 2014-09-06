#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import cgi

log = logging.getLogger(__name__)


def to_html(plain):
    html = cgi.escape(plain).replace('\n', '<br />')


class Message:
    def __init__(self, plain, destination, html=None):
        self.plain = plain
        self.html = html or to_html(plain)
        self.destination = destination


class CardboardMessage:
    def __init__(self, connection, default_destination):
        self.connection = connection
        self.default_destination = default_destination

    def create_message(self, plaintext, html=None, destination=None):
        message = Message(plaintext, html, destination or self.default_destination)
        return message

    def send_message(self, message=None, type="groupchat"):
        log.debug("Sending message: %s" % message.plain)
        log.debug("Destination: %s, type: %s" % (message.destination, type))
        self.connection.send_message(mto=message.destination,
                                     mbody=message.plain,
                                     mhtml=message.html,
                                     mtype=type)