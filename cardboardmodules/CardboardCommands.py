#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import requests
import random

log = logging.getLogger(__name__)


class CardboardCommands:
    def __init__(self, db):
        self.db = db

    def get_all_nicks_in_room(self, connection):
        nicklist = connection.plugin['xep_0045'].getRoster(connection.channel)
        return nicklist

    def get_all_jids_in_room(self, connection):
        nicklist = self.get_all_nicks(connection)
        jidlist = []
        for nick in nicklist:
            jid = self.get_user_jid(connection, nick)
            jidlist.append(jid.bare)
        return jidlist

    def goodtuch(self, nick):
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

    def badtuch(self, nick):
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

    def sextuch(self, nick):
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

    def tuch(self, nick, body):
        """Someone does something to me, decide what to do with them"""
        log.debug("Getting actions from database")
        niceActions = self.db.get_actions("nice")
        sexActions = self.db.get_actions("sex")

        if "pets" in body.lower():
            log.debug("%s is petting me!" % nick)
            return "/me purrs :sweetiepleased:"
        if [i for i in niceActions if i in body.lower()]:
            log.debug("%s is doing nice things to me!" % nick)
            return self.goodtuch(nick)
        if [i for i in sexActions if i in body.lower()]:
            log.debug("%s is doing sex things to me!" % nick)
            return self.sextuch(nick)
        else:
            log.debug("%s is doing bad things to me!" % nick)
            return self.badtuch(nick)

    def get_user_affiliation(self, connection, nick):
        """Get a user's affiliation with the room"""
        useraffiliation = connection.plugin['xep_0045'].getJidProperty(connection.channel, nick, 'affiliation')
        return useraffiliation

    def get_user_jid(self, connection, nick):
        """Get the JID from a user based on their nick"""
        userjid = connection.plugin['xep_0045'].getJidProperty(connection.channel, nick, 'jid')
        return userjid

    def get_user_role(self, connection, nick):
        """Get a user's affiliation with the room"""
        userrole = connection.plugin['xep_0045'].getJidProperty(connection.channel, nick, 'role')
        return userrole

    def kick_user(self, connection, nick, sender):
        """Kick a user from the room"""
        senderrole = self.get_user_role(connection, sender)
        receiverrole = self.get_user_role(connection, nick)
        if receiverrole is None:
            log.debug("Kick requested by %s failed because target %s is not in the room" % (sender, nick))
            return "I'm sorry, %s, I can't find %s in the room. :sweetiestare:" % (sender, nick)
        if senderrole != 'moderator':
            log.debug("Kick requested by %s failed because they are not a moderator" % sender)
            return "I'm sorry, %s, I can't find %s in the room. :sweetiestare:" % (sender, nick)
        if receiverrole == 'moderator':
            log.debug("Kick requested by %s failed because target %s is a moderator" % (sender, nick))
            return "I'm sorry, %s, I can't find %s in the room. :sweetiestare:" % (sender, nick)
        userjid = self.get_user_jid(connection, nick)
        log.debug("Attempting to kick %s" % nick)
        try:
            kick = connection.plugin['xep_0045'].setRole(connection.channel, nick=nick, role="none")
            if kick:
                log.debug("Kicking of %s successful" % nick)
                return "%s was kicked. :sweetiestare:"
            else:
                log.debug("Kicking of %s failed" % nick)
                return "I could not kick %s, maybe do it yourself instead? :sweetiestare:" % nick
        except Exception as e:
            log.warning("Exception raised while kicking %s!" % nick)
            log.warning("Exception was: %s" % str(e))
            pass

    def argue(self):
        """Tumblr-argueing thanks to Nyctef and his TumblrAAS"""
        try:
            res = requests.get('http://tumblraas.azurewebsites.net/', timeout=5)
            return res.text.strip()
        except RequestException as e:
            log.warning("Exception while arguing: %s" % str(e))
            return "Huh, what? I zoned out for a moment there."

    def rant(self):
        """Tumblr-rants thanks to Nyctef and his TumblrAAS"""
        try:
            res = requests.get('http://tumblraas.azurewebsites.net/rant', timeout=5)
            return res.text.strip()
        except RequestException as e:
            log.warning("Exception while arguing: %s" % str(e))
            return "Huh, what? I zoned out for a moment there."

    def ceedee(self):
        """Confirm or deny"""
        return random.choice(['c', 'd'])

    def roll_dice(self, dice, sides):
        try:
            return [random.randint(1, sides) for i in range(dice)]
        except Exception as e:
            log.warning("Exception in diceroll: %s" % str(e))
            return []

    def roll(self, message):
        if message.lower() == "out":
            return "/me transforms and rides off :rdsanic:"
        try:
            dice, sides = list(map(int, message.split('d', 1)))
            log.debug("Diceroll requested with %s dice and %s sides" % (dice, sides))
        except:
            log.warning("Bad dice!")
            return "Sorry, can't parse your input"
        if dice > 50:
            return "I can't roll that many dice."
        if sides > 200:
            return "I don't have any dice with that many sides."
        if sides < 2:
            return "How can you roll a dice without sides?"
        if dice < 1:
            return "I can't roll less than one dice."
        diceroll = self.roll_dice(dice, sides)
        if not diceroll:
            return "Oops, I accidentally dropped my dice"
        reply = ', '.join(map(str, diceroll))
        if sides == 6:
            # assuming Shadowrun roll
            success = sum(i >= 5 for i in diceroll)
            reply = reply + " (%s success)" % success
            if sum(i == 1 for i in diceroll) > dice / 2:
                if not success:
                    reply = reply + " CRITICAL GLITCH"
                else:
                    reply = reply + " glitched"
        return reply