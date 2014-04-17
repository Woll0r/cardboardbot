#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import config # Get config

import random
import logging
import re
import urllib
import requests

# Needed for reading the memories file
#import yaml

# Needed for loading the brain files
#import aiml
#import os.path

# Needed for logging into SQLite
import sqlite3
import time

def imgur_filter(link):
    """Convert Imgur image links into their full fledged counterparts"""
    imgurregex = re.compile(r'^http(s)?://i.imgur.com/([a-zA-Z0-9]*)\..*$')
    match = imgurregex.match(link)
    if (match):
        replacement = 'http://imgur.com/'+match.group(2)
        logging.debug("replacing "+link+" with "+replacement)
        return replacement
    return link

def e621_filter(link):
    """Convert e621 image links into their full fledged counterparts"""
    e621regex = re.compile(r'http(s)?://static([0-9]*).e621.net/data(/sample)?.*?((?:[a-z0-9][a-z0-9]*[a-z0-9][a-z0-9]+[a-z0-9]*))')
    match = e621regex.match(link)
    if (match):
        replacement = 'https://e621.net/post/show?md5='+match.group(4)
        logging.debug("replacing "+link+" with "+replacement)
        return replacement
    return link
    

def create_table():
    try:
        con = sqlite3.connect('cardboardlog.db', isolation_level=None)
        cur = con.cursor()
    
        cur.execute("DROP TABLE IF EXISTS cardboardlinks")
        cur.execute("CREATE TABLE cardboardlinks(id INTEGER PRIMARY KEY, timestamp INTEGER, name TEXT, url TEXT, title TEXT);")
    except sqlite3.Error, e:    
        print "Error %s:" % e.args[0]
        exit(1)
    
    finally:
        if con:
            con.close()

def handle_message(timestamp, sender, body):
    """Handle URL's and get titles from the pages"""
    urlregex = re.compile(
        r"((([A-Za-z]{3,9}:(?:\/\/)?)(?:[-;:&=\+\$,\w]+@)?[A-Za-z0-9.-]+|(?:www.|[-;:&=\+\$,\w]+@)[A-Za-z0-9.-]+)((?:\/[\+~%\/.\w_-]*)?\??(?:[-\+=&;%@.\w_]*)#?(?:[\w]*))?)")
    matches = urlregex.findall(body)
    matches = map(lambda x: x[0], matches)
    matches = map(imgur_filter, matches)
    matches = map(e621_filter, matches)
    # matches = map(deviantart_filter, matches)                      # Doesn't work properly and makes normal ones barf.
    if matches:
        logging.debug("I think I see an URL! " + " / ".join(matches))

        for match in matches:
            title = handle_url(match)
            if title is None:
                print "Not a valid URL!"
            elif title:
                print "TIMESTAMP: ", timestamp
                print "SENDER: ", sender
                print "URL: ", match
                print "TITLE: ", title, "\n"
                insert_in_linktable(timestamp, sender, match, title)
            else:
                print "TIMESTAMP: ", timestamp
                print "SENDER: ", sender
                print "URL: ", match
                print "TITLE: ", match
                insert_in_linktable(timestamp, sender, match, match)

def insert_in_linktable(timestamp, sender, url, title):
    try:
        con = sqlite3.connect('cardboardlog.db')
        cur = con.cursor()
        cmd = "INSERT INTO cardboardlinks(timestamp, name, url, title) VALUES(?, ?, ?, ?);"
        cur.execute(cmd, (timestamp, sender, url, title))
    except sqlite3.Error as e:
        if con:
            con.rollback()
        logging.critical("Fatal error in SQLite processing: %s" % e.args[0])
        exit(1)
    finally:
        if con:
            con.commit()
            con.close() 

def handle_url(match):
    from bs4 import BeautifulSoup
    try:
        res = requests.get(match, timeout=5)
        if not 'html' in res.headers['content-type']:
            logging.debug("%s isn't HTML!" % match)
            return False
        soup = BeautifulSoup(res.text)
        return soup.title.string.strip()
    except Exception as e:
        logging.debug("Error fetching url "+match+" : "+str(e))
        return None
    if not len(results):
        # no results
        return None

def fetch_messages():
    try:
        con = sqlite3.connect('cardboardlog.db', isolation_level=None)
        cur = con.cursor()
        
        cur.execute("SELECT * FROM cardboardlog")
        result = cur.fetchall();
        
    except sqlite3.Error, e:
        print "Error %s:" % e.args[0]
        exit(1)
    finally:
        if con:
            con.close()

    return result
        
# Setup logging.
logging.basicConfig(level=logging.ERROR,
                        format='%(levelname)-8s %(message)s')

create_table()
                        
results = fetch_messages()

for row in results:
    handle_message(row[1], row[2], row[3])