#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import time

log = logging.getLogger(__name__)


class CardboardPresenceHandler:
    def __init__(self, db):
        log.debug("CardboardPresenceHandler init")
        self.db = db

    def handler(self, presence):
        log.debug("Presence received!")
        nick = presence['muc']['nick']
        jid = presence['muc']['jid']
        timestamp = int(time.time())
        presencetype = presence['type']

        if presencetype is 'unavailable':
            log.info("%s just went offline! Saving current time..." % nick)
            self.db.update_presence(nick, jid, timestamp)
        