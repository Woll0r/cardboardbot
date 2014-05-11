#!/usr/bin/env python
# -*- coding: utf-8 -*-

import config # Get config

# Needed for logging into SQLite
import sqlite3
import time

log = logging.getLogger(__name__)

def get_actions(type):
    actions = []
    con = sqlite3.connect('/home/wolfgang/cardboardenv/cardboardbot/cardboardlog.db')
    cur = con.cursor()
    cmd = "SELECT action FROM cardboardactions WHERE type=?;"
    cur.execute(cmd, (type, ))
    results = c.fetchall()
    for action in results:
        actions.append(action[0])
    c.close()

def insert_into_messages_table(timestamp, nick, jid, message):
	try:
        con = sqlite3.connect('cardboardlog.db')
        cur = con.cursor()
        cmd = "INSERT INTO cardboardlog(timestamp, name, message) VALUES(?, ?, ?);"
        if len(name):
            cur.execute(cmd, (timestamp, jid, message))
            log.debug("Written to database!")
            log.debug("Checking if name is in the database...")
            cmd = "SELECT * FROM cardboardnick WHERE jid = ?;"
            cur.execute(cmd, (userjid, ))
            namecheck = cur.fetchone()
            if namecheck is None:
                log.debug("Name doesn't exist.")
                cmd = "INSERT INTO cardboardnick(jid, nick) VALUES(?, ?);"
                cur.execute(cmd, (userjid, nick))
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
			
def insert_in_link_table(timestamp, sender, url, title):
    try:
        con = sqlite3.connect('cardboardlog.db')
        cur = con.cursor()
        cmd = "INSERT INTO cardboardlinks(timestamp, name, url, title) VALUES(?, ?, ?, ?);"
        cur.execute(cmd, (timestamp, sender, url, title))
    except sqlite3.Error as e:
        if con:
            con.rollback()
        log.critical("Fatal error in SQLite processing: %s" % e.args[0])
        exit(1)
    finally:
        if con:
            con.commit()
            con.close() 