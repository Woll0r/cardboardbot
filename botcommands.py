#!/usr/bin/env python
# -*- coding: utf-8 -*-

import config # Get config
import random
import logging

def handler(connection, msg):
    if msg["mucnick"] == connection.nick:
        return

    if connection.nick in msg["body"]:
        logging.debug("Someone said my name!")
        connection.send_message(mto=msg["from"].bare,
                                mbody="Beep boop, %s!" % msg["mucnick"],
                                mtype="groupchat")
        return
