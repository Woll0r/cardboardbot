#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""CardboardCommands module for all the chat commands defined in the bot"""

import logging
import random
import requests
import datetime


log = logging.getLogger(__name__)


class CardboardCommands(object):
    """CardboardCommands class for handling all bot commands"""

    def __init__(self, database, connection, iq):
        log.debug("CardboardCommands init")
        self._db = database
        self._connection = connection
        self._iq = iq

    ###########################################################################
    # Nickname specific commands

    def get_all_nicks_in_room(self):
        """Fetch all the nicknames for people that are currently in the room"""
        nicklist = self._connection.plugin['xep_0045'].getRoster(
            self._connection.channel)
        return nicklist

    def get_all_jids_in_room(self):
        """Fetch all the JIDs for people that are currently in the room"""
        nicklist = self.get_all_nicks_in_room()
        jidlist = []
        for nick in nicklist:
            jid = self.get_user_jid(nick=nick)
            jidlist.append(jid.bare)
        return jidlist
    
    ###########################################################################
    # Touches

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
        nice_actions = self._db.get_actions(actiontype="nice")
        sex_actions = self._db.get_actions(actiontype="sex")

        if "pets" in body.lower():
            log.debug("%s is petting me!", nick)
            return "/me purrs :sweetiepleased:"
        if [i for i in nice_actions if i in body.lower()]:
            log.debug("%s is doing nice things to me!", nick)
            return self.goodtuch(nick=nick)
        if [i for i in sex_actions if i in body.lower()]:
            log.debug("%s is doing sex things to me!", nick)
            return self.sextuch(nick=nick)
        else:
            log.debug("%s is doing bad things to me!", nick)
            return self.badtuch(nick=nick)

    ###########################################################################
    # User affiliation commands (kick, ban, unban, moderator status, etc)

    def get_user_affiliation(self, nick):
        """Get a user's affiliation with the room"""
        useraffiliation = self._connection.plugin['xep_0045'].getJidProperty(
            self._connection.channel, nick, 'affiliation')
        return useraffiliation

    def get_user_jid(self, nick):
        """Get the JID from a user based on their nick"""
        userjid = self._connection.plugin['xep_0045'].getJidProperty(
            self._connection.channel, nick, 'jid')
        return userjid

    def get_user_role(self, nick):
        """Get a user's affiliation with the room"""
        userrole = self._connection.plugin['xep_0045'].getJidProperty(
            self._connection.channel, nick, 'role')
        return userrole

    def kick_user(self, nick, sender):
        """Kick a user from the room"""
        senderrole = self.get_user_role(nick=sender)
        receiverrole = self.get_user_role(nick=nick)
        if senderrole != 'moderator':
            log.debug("Kick requested by %s " +
                      "failed because they are not a moderator", sender)
            return "I'm sorry, %s, I can't let " + \
                "you do that. :sweetiestare:" % (sender, )
        if receiverrole is None:
            log.debug("Kick requested by %s " +
                      "failed because target %s is not in the room",
                      sender, nick)
            return "I'm sorry, %s, I can't find %s " + \
                   "in the room. :sweetiestare:" % (sender, nick)
        if receiverrole == 'moderator':
            log.debug("Kick requested by %s " +
                      "failed because target %s is a moderator",
                      sender, nick)
            return "I'm sorry, %s, I can't do that. " + \
                ":sweetiestare:" % (sender, )
        log.debug("Attempting to kick %s", nick)

        kick = self._connection.plugin['xep_0045'].setRole(
            self._connection.channel, nick=nick, role="none")
        if kick:
            log.debug("Kicking of %s successful", nick)
            return "%s was kicked. :sweetiestare:" % nick
        else:
            log.debug("Kicking of %s failed", nick)
            return "I could not kick %s, " + \
                   "maybe do it yourself instead? :sweetiestare:" % nick

    def banlist(self):
        return self._iq.banlist()

    ###########################################################################
    # Tumblr as a service commands
     
    def argue(self):
        """Tumblr-argueing thanks to Nyctef and his TumblrAAS"""
        try:
            res = requests.get('http://tumblraas.azurewebsites.net/',
                               timeout=5)
            return res.text.strip()
        except requests.RequestException as ex:
            log.warning("Exception while arguing: %s", str(ex))
            return "Huh, what? I zoned out for a moment there."

    def rant(self):
        """Tumblr-rants thanks to Nyctef and his TumblrAAS"""
        try:
            res = requests.get('http://tumblraas.azurewebsites.net/rant',
                               timeout=5)
            return res.text.strip()
        except requests.RequestException as ex:
            log.warning("Exception while arguing: %s", str(ex))
            return "Huh, what? I zoned out for a moment there."

    ###########################################################################
    # Confirm or deny
    
    def ceedee(self):
        """Confirm or deny"""
        return random.choice(['c', 'd'])

    ###########################################################################
    # Dice roller
    
    def roll_dice(self, dice, sides):
        """Perform the actual rolling of the dice"""
        return [random.randint(1, sides) for i in list(range(dice))]

    def roll(self, message):
        """ Rolls dice, up to 63 dice with 100 sides"""
        if message.lower() == "out":
            return "/me transforms and rides off :rdsanic:"
        try:
            dice, sides = list(int(x) for x in message.split('d', 1))
            log.debug("Diceroll requested with %s dice and %s sides",
                      dice, sides)
        except ValueError:
            log.warning("Bad dice!")
            return "Sorry, can't parse your input"
        if dice > 63:
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
        reply = ', '.join(str(x) for x in diceroll)
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

    ###########################################################################
    # Last seen/last said command

    def seen(self, nick):
        """Look up when a user last logged off"""
        jid = self.get_user_jid(nick)

        if jid:
            return "%s is in the room right now!" % nick

        result = self._db.get_last_logoff(nick)

        if result is None:
            return "I'm sorry, I have no idea who %s is." % nick
        elif result == 0:
            return "I'm sorry, I have no idea when %s last logged off." % nick
        else:
            timestamp = datetime.datetime.fromtimestamp(result)
            timestring = timestamp.strftime("%d %b %Y %H:%M:%S")
            return "%s last logged off at %s" % (nick, timestring)

    def lastsaid(self, nick):
        """Look up when a user last said something"""
        result = self._db.get_last_message(nick)

        if result is None:
            return "I'm sorry, I have never heard %s speak." % nick
        else:
            timestamp = datetime.datetime.fromtimestamp(result[0])
            timestring = timestamp.strftime("%d %b %Y %H:%M:%S")
            message = result[1]
            return "At %s, %s said \"%s\"" % (timestring, nick, message)

    ###########################################################################
    # Sudo
    
    def sudo(self, message):
        """Execute a command with sudo privileges"""
        if self.get_user_role(message.sendernick) != 'moderator':
            return 'User %s is not in the sudoers file. ' + \
                'This incident will be reported.'
        else:
            return 'This command should not be run as root.' \
                'Please execute this command without sudo.'
    