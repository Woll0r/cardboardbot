#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

# Needed for logging into SQLite
import sqlite3

log = logging.getLogger(__name__)


class CardboardDatabase:
    def __init__(self, databasefile='cardboardlog.db'):
        log.debug("CardboardDatabase init")
        self.path = databasefile

    def get_actions(self, type):
        actions = []
        try:
            con = sqlite3.connect(self.path)
            cur = con.cursor()
            cmd = "SELECT action FROM cardboardactions WHERE type=?;"
            cur.execute(cmd, (type, ))
            results = cur.fetchall()
            for action in results:
                actions.append(action[0])
        except sqlite3.Error as e:
            if con:
                con.rollback()
            log.warning("Error in SQLite processing: %s" % e.args[0])
        finally:
            if con:
                con.close()
        return actions

    def insert_in_messages_table(self, timestamp, nick, jid, message):
        try:
            con = sqlite3.connect(self.path)
            cur = con.cursor()
            cmd = "INSERT INTO cardboardlog(timestamp, name, message) VALUES(?, ?, ?);"
            if len(nick):
                cur.execute(cmd, (timestamp, jid, message))
                log.debug("Written to database!")
                log.debug("Checking if name is in the database...")
                cmd = "SELECT * FROM cardboardnick WHERE jid = ?;"
                cur.execute(cmd, (jid, ))
                namecheck = cur.fetchone()
                if namecheck is None:
                    log.debug("Name doesn't exist.")
                    cmd = "INSERT INTO cardboardnick(jid, nick) VALUES(?, ?);"
                    cur.execute(cmd, (jid, nick))
                    logging.debug("Name not found in database, inserted!")
                else:
                    log.debug("This person exists in the database")
        except sqlite3.Error as e:
            if con:
                con.rollback()
            log.critical("Fatal error in SQLite processing: %s" % e.args[0])
            exit(1)
        finally:
            if con:
                con.commit()
                con.close()

    def insert_in_link_table(self, timestamp, sender, url, title, domain):
        try:
            con = sqlite3.connect(self.path)
            cur = con.cursor()
            cmd = "INSERT INTO cardboardlinks(timestamp, name, url, title, domain) VALUES(?, ?, ?, ?, ?);"
            cur.execute(cmd, (timestamp, sender, url, title, domain))
        except sqlite3.Error as e:
            if con:
                con.rollback()
            log.critical("Fatal error in SQLite processing: %s" % e.args[0])
            exit(1)
        finally:
            if con:
                con.commit()
                con.close() 