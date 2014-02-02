#!/usr/bin/env python
# -*- coding: utf-8 -*-

import config # Get config

import random
import logging
import re
import urllib
import requests

# Needed for reading the memories file
import yaml

# Needed for loading the brain files
import aiml
import os.path

# Initialize Alice
brain = aiml.Kernel()

niceActions = ["snuggles", "cuddles", "kisses", "kissies", "nuzzles", "hugs", "loves", "licks", "rubs", "sniffs", "paws", "earnoms", "smooches", "walks up to", "looks at"]
sexActions = ["yiffs", "rapes", "sexes", "fingers", "fucks", "humps"]

def argue():
    """Tumblr-rant"""
    res = requests.get('http://tumblraas.azurewebsites.net/', timeout=5)
    return res.text.strip()

def rant():
    """Tumblr-rants"""
    res = requests.get('http://tumblraas.azurewebsites.net/rant', timeout=5)
    return res.text.strip()

def ceedee():
    """Confirm or deny"""
    return random.choice(['c', 'd'])

def brain_start():
    """Creates the brain file if needed and then loads it.
    Afterwards, the memories will be loaded so the bot gets her identity"""
    if os.path.isfile("standard.brn"):
	    # Brain is available, load it
        logging.info("Found my brain, loading it now!")
        brain.bootstrap(brainFile = "standard.brn")
    else:
	    # No brain file, so we create one.
        logging.info("Didn't find my brain, generating a new one!")
        brain.bootstrap(learnFiles = "aiml/std-startup.xml", commands = "load aiml b")
        brain.saveBrain("standard.brn")
    logging.info("Brain loaded. Now setting all my memories!")
    memoryfile = file('personality.yaml', 'r')
    memories = yaml.load(memoryfile)
    for k, v in memories.items():
        brain.setBotPredicate(k, v)

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
    e621regex = re.compile(r'http(s)?://static([0-9]*).e621.net.*?((?:[a-z][a-z]*[0-9]+[a-z0-9]*))')
    match = e621regex.match(link)
    if (match):
        replacement = 'https://e621.net/post/show?md5='+match.group(3)
        logging.debug("replacing "+link+" with "+replacement)
        return replacement
    return link

def goodtuch(nick):
    """Someone touches the bot in a nice way"""
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
               "/me kisses %s",
               "/me licks %s"]
    return random.choice(actions) % nick + " " + random.choice(emotes)

def badtuch(nick):
    """Someone touches the bot in a bad way"""
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

def sextuch(nick):
    """Someone touches the bot in a sexual way"""
    emotes = [":sweetiecrack:",
              ":sweetiedesk:",
              ":sweetiedust:",
              ":sweetielod:",
              ":sweetiemad:",
              ":sweetietwitch:"]
    actions = ["/me sticks a broken glass bottle into %s's ass",
               "/me inserts red hot metal pokers into %s's orifices",
               "/me electrocutes %s",
               "/me tosses %s's soap into a prison shower"]
    return random.choice(actions) % nick + " " + random.choice(emotes)

def tuch(nick, body):
    """Someone does something to me, decide what to do with them"""
    if "pets" in body.lower():
        logging.debug("%s is petting me!" % nick)
        return "/me purrs :sweetiepleased:"
    if [i for i in niceActions if i in body.lower()]:
        logging.debug("%s is doing nice things to me!" % nick)
        return goodtuch(nick)
    if [i for i in sexActions if i in body.lower()]:
        logging.debug("%s is doing sex things to me!" % nick)
        return sextuch(nick)
    else:
        logging.debug("%s is doing bad things to me!" % nick)
        return badtuch(nick)
    
def alicemessage(nick, body):
    logging.debug("I don't know what %s is saying, so I'll let Alice respond for me!" % nick)
    if body.startswith(config.nick + ": "):
        body = body.replace(config.nick + ": ", "", 1)
    
    body.replace(config.nick, "you")

    resp = brain.respond(body, nick)
    return resp
    
def handle_url(body):
    """Handle URL's and get titles from the pages"""
    urlregex = re.compile(
        r"((([A-Za-z]{3,9}:(?:\/\/)?)(?:[-;:&=\+\$,\w]+@)?[A-Za-z0-9.-]+|(?:www.|[-;:&=\+\$,\w]+@)[A-Za-z0-9.-]+)((?:\/[\+~%\/.\w_-]*)?\??(?:[-\+=&;%@.\w_]*)#?(?:[\w]*))?)")
    matches = urlregex.findall(body)
    matches = map(lambda x: x[0], matches)
    matches = map(imgur_filter, matches)
    matches = map(e621_filter, matches)
    if matches:
        logging.debug("I think I see an URL! " + " / ".join(matches))
        results = []
        from bs4 import BeautifulSoup
        for match in matches:
            try:
                res = requests.get(match, timeout=5)
                if not 'html' in res.headers['content-type']:
                    logging.debug("%s isn't HTML!" % match)
                    break
                soup = BeautifulSoup(res.text)
                results.append(soup.title.string.strip())
            except Exception as e:
                logging.debug("Error fetching url "+match+" : "+str(e))
                pass
        if not len(results):
            # no results
            return False
        result = " / ".join(results).strip()
        return result

def handler(connection, msg):
    """Handle incoming messages"""
    fullmessage = msg["mucnick"].ljust(25) + ": " + msg["body"]
    logging.info(fullmessage)

    with open("cardboardbot.log", "a") as logfile:
        logfile.write(fullmessage + "\n")
    
    if msg["mucnick"] == connection.nick:
        return

    if connection.nick.lower() in msg["body"].lower():
        logging.debug("Someone said my name!")

        # C/D mode
        if msg["body"].lower().endswith("c/d") or msg["body"].lower().endswith("c/d?"):
            connection.send_message(mto=msg["from"].bare,
                                    mbody="%s: %s" %(msg["mucnick"], ceedee()),
                                    mtype="groupchat")
            return
        
        # Someone does things to me!
        if msg["body"].lower().startswith("/me"):
            logging.debug("I am being touched by %s!" % msg["mucnick"])
            connection.send_message(mto=msg["from"].bare, mbody=tuch(msg["mucnick"], msg["body"]), mtype="groupchat")
            return
            
        
        # Tumblr rant
        if "argue" in msg["body"].lower():
            logging.debug("Someone wants me to argue!")
            connection.send_message(mto=msg["from"].bare, mbody=argue(), mtype="groupchat")
            return

        if "rant" in msg["body"].lower():
            logging.debug("Someone wants me to rant!")
            connection.send_message(mto=msg["from"].bare, mbody=rant(), mtype="groupchat")
            return

        # Delegate response to Alice
        connection.send_message(mto=msg["from"].bare, mbody=alicemessage(msg["mucnick"], msg["body"]), mtype="groupchat")
        return

    links = handle_url(msg["body"])
    if links:
        connection.send_message(mto=msg["from"].bare, mbody=links, mtype="groupchat")
        
    return