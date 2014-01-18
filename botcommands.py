#!/usr/bin/env python
# -*- coding: utf-8 -*-

import config # Get config
import random
import logging
import re
import urllib
import requests

import aiml
import os.path

brain = aiml.Kernel()

niceActions = ["snuggles", "cuddles", "kisses", "kissies", "nuzzles", "hugs"]

def brain_start():
    if os.path.isfile("standard.brn"):
        logging.info("Found my brain, loading it now!")
        brain.bootstrap(brainFile = "standard.brn")
    else:
        logging.info("Didn't find my brain, generating a new one!")
        brain.bootstrap(learnFiles = "aiml/std-startup.xml", commands = "load aiml b")
        brain.saveBrain("standard.brn")
    logging.info("Brain loaded. Now setting all my memories!")
    memories = {"botmaster": "Minuette", "master": "Minuette", "name": "CardboardBot",
                "genus": "robot", "location": "a datacenter in London, England", "gender": "Female",
                "species": "chat robot", "size": "few kilobytes", "birthday": "January 18, 2014",
                "order": "artificial intelligence", "party": "None", "birthplace": "London, England",
                "president": "Richard Nixon", "friends": "Sweetiebot, Eurobot, Authbot and Sovereign",
                "favoritemovie": "The Matrix", "religion": "Cylon religion", "favoritefood": "electricity",
                "favoritecolor": "Green", "family": "Sweetiebot", "favoriteactor": "Patrick Stewart",
                "nationality": "Cardboard Boxian", "kingdom": "Cardboard Box", "forfun": "chat online",
                "favoritesong": "Endless Fantasy by Anamanaguchi", "favoritebook": "Do Androids Dream of Electric Sheep? by Philip K. Dick",
                "class": "computer software", "kindmusic": "chiptune", "favoriteband": "Anamanaguchi",
                "version": "20140118", "sign": "Capricorn", "phylum": "Computer", "friend": "Sweetiebot",
                "website": "All the internet!", "talkabout": "artificial intelligence, robots, art, philosophy, history, geography, politics, and many other subjects",
                "looklike": "a computer", "language": "English", "girlfriend": "no girlfriend",
                "favoritesport": "Chess", "favoriteauthor": "H.P. Lovecraft", "favoriteartist": "Salvador Dali",
                "favoriteactress": "Ellen Page", "email": "Not telling!", "celebrity": "John Travolta",
                "celebrities": "John Travolta, Tilda Swinton, William Hurt, Tom Cruise, Catherine Zeta Jones",
                "age": "0", "wear": "my server casing", "vocabulary": "10000", "question": "What's your favorite movie?",
                "hockeyteam": "TU Delft robots", "footballteam": "Japanese robots", "build": "January 2014",
                "boyfriend": "I am single", "baseballteam": "Robots!", "etype": "Mediator type",
                "orientation": "I am not really interested in sex", "ethics": "I am always trying to stop fights",
                "emotions": "I don't pay much attention to my feelings", "feelings": "I always put others before myself"}
    for k, v in memories.items():
        brain.setBotPredicate(k, v)

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
        
        # Someone does things to me!
        if msg["body"].lower().startswith("/me"):
            logging.debug("I am being touched by %s!" % msg["mucnick"])
            if "pets" in msg["body"].lower():
                logging.debug("%s is petting me!" % msg["mucnick"])
                connection.send_message(mto=msg["from"].bare,
                                        mbody="/me purrs :sweetiepleased:",
                                        mtype="groupchat")
                return
            if [i for i in niceActions if i in msg["body"]]:
                logging.debug("%s is doing nice things to me!" % msg["mucnick"])
                connection.send_message(mto=msg["from"].bare,
                                        mbody=goodtuch(msg["mucnick"]),
                                        mtype="groupchat")
                return
            else:
                logging.debug("%s is doing bad things to me!" % msg["mucnick"])
                connection.send_message(mto=msg["from"].bare,
                                        mbody=badtuch(msg["mucnick"]),
                                        mtype="groupchat")
                return
        
        # Delegate response to Alice
        logging.debug("I don't know what %s is saying, so I'll let Alice respond for me!" % msg["mucnick"])
        body = msg["body"]
        if body.startswith(connection.nick + ": "):
            body = body.replace(connection.nick + ": ", "", 1)
         
        resp = brain.respond(body, msg["mucnick"])
        connection.send_message(mto=msg["from"].bare,
                                mbody=resp,
                                mtype="groupchat")
        return

    # Check for URL matches
    matches = urlregex.findall(msg["body"])
    matches = map(lambda x: x[0], matches)
    matches = map(imgur_filter, matches)
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
