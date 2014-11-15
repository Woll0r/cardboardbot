#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

log = logging.getLogger(__name__)


class CardboardDummyBrain:
    def __init__(self):
        log.debug("CardboardDummyBrain init")

    def response(self, nick, body):
        log.debug("Dummy response!")

        resp = "Hello, " + nick + "! My brain was replaced with a piece of string :rdderp:"

        return resp