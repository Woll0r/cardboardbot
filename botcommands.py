#!/usr/bin/env python
# -*- coding: utf-8 -*-

import config # Get config
import random
import logging
import re
import urllib
import requests

niceActions = ["snuggles", "cuddles", "kisses", "kissies", "nuzzles", "hugs"]

def imgur_filter(link):
    imgurregex = re.compile(r'^http(s)?://i.imgur.com/([a-zA-Z0-9]*)\..*$')
    match = imgurregex.match(link)
    if (match):
        replacement = 'http://imgur.com/'+match.group(2)
        logging.debug("replacing "+link+" with "+replacement)
        return replacement
    return link

def goodtuch(nick):
    emotes = [":sweetie:",
              ":sweetiecreep:",
              ":sweetieglee:",
              ":sweetieidea:",
              ":sweetiepleased:",
              ":sweetieshake:"]
    actions = ["/me nuzzles %s",
               "/me snuggles %s",
               "/me cuddles %s",
               "/me hugs %s",
               "/me kisses %s"]
    return random.choice(actions) % nick + " " + random.choice(emotes)

def badtuch(nick):
    emotes = [":sweetiecrack:",
              ":sweetiedesk:",
              ":sweetiedust:",
              ":sweetielod:",
              ":sweetiemad:",
              ":sweetietwitch:"]
    actions = ["/me defenestrates %s",
               "/me hits %s with a spiked stick",
               "/me electrocutes %s",
               "/me throws %s into a bottomless pit",
               "/me teleports %s into space"]
    return random.choice(actions) % nick + " " + random.choice(emotes)

def handler(connection, msg):
    urlregex = re.compile(
        r"((([A-Za-z]{3,9}:(?:\/\/)?)(?:[-;:&=\+\$,\w]+@)?[A-Za-z0-9.-]+|(?:www.|[-;:&=\+\$,\w]+@)[A-Za-z0-9.-]+)((?:\/[\+~%\/.\w_-]*)?\??(?:[-\+=&;%@.\w_]*)#?(?:[\w]*))?)")
    
    if msg["mucnick"] == connection.nick:
        return

    if connection.nick.lower() in msg["body"].lower():
        logging.debug("Someone said my name!")

        if msg["body"].lower().startswith("/me"):
            if "pets" in msg["body"].lower():
                connection.send_message(mto=msg["from"].bare,
                                        mbody="/me purrs :sweetiepleased:",
                                        mtype="groupchat")
                return
            logging.debug([i for i in niceActions if i in msg["body"]])
            if [i for i in niceActions if i in msg["body"]]:
                connection.send_message(mto=msg["from"].bare,
                                        mbody=goodtuch(msg["mucnick"]),
                                        mtype="groupchat")
                return
            else:
                connection.send_message(mto=msg["from"].bare,
                                        mbody=badtuch(msg["mucnick"]),
                                        mtype="groupchat")
                return
        
        connection.send_message(mto=msg["from"].bare,
                                mbody="Beep boop, %s!" % msg["mucnick"],
                                mtype="groupchat")
        return

    # Check for URL matches
    matches = urlregex.findall(msg["body"])
    matches = map(lambda x: x[0], matches)
    matches = map(imgur_filter, matches)
    if matches:
        logging.debug("URL-matching! " + " / ".join(matches))
        results = []
        from bs4 import BeautifulSoup
        for match in matches:
            try:
                res = requests.get(match, timeout=5)
                if not 'html' in res.headers['content-type']:
                    logging.debug("Skipping non-HTML link result")
                    break
                soup = BeautifulSoup(res.text)
                results.append(soup.title.string)
            except Exception as e:
                logging.debug("Error fetching url "+match+" : "+str(e))
                pass
        if not len(results):
            # no results
            return
        result = " / ".join(results).strip()
        connection.send_message(mto=msg["from"].bare,
                                mbody=result,
                                mtype="groupchat")
        return
