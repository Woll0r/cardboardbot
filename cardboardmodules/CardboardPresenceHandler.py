#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""CardboardPresenceHandler module for handling presence in a group chat"""

import logging
import time

log = logging.getLogger(__name__)


class CardboardPresenceHandler(object):
    """CardboardPresenceHandler class for handling presence in a group chat"""
    def __init__(self, database):
        log.debug("CardboardPresenceHandler init")
        self._db = database

    def handler(self, presence):
        """Handle presence events"""
        log.debug("Presence received!")
        nick = str(presence['muc']['nick'])
        jid = presence['muc']['jid']
        barejid = jid.bare
        timestamp = int(time.time())
        presencetype = presence['type']

        if presencetype == 'unavailable':
            if barejid and barejid != '':
                log.info("%s just went offline! Saving current time...", nick)
                self._db.update_presence(nick, barejid, timestamp)
