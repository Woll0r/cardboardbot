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
        nick = str(presence['muc']['nick'])
        jid = presence['muc']['jid']
        barejid = jid.bare
        timestamp = int(time.time())
        presencetype = presence['type']

        if presencetype == 'unavailable':
            if barejid and barejid != '':
                log.info("%s just went offline! Saving current time..." % nick)
                self.db.update_presence(nick, barejid, timestamp)
        
