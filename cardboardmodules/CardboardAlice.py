#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""CardboardAlice module for all AI involving Alice (AIML) chat routines"""

import logging

# Needed for reading the memories file
import yaml

# Needed for loading the brain files
import aiml
import os.path

log = logging.getLogger(__name__)


class CardboardAlice(object):
    """CardboardAlice class for interacting using Alice (AIML) routines"""
    def __init__(self, brainfile, memoriesfile, aimlpath, nick):
        log.debug("CardboardAlice init")
        # Initialize Alice
        self.brain = aiml.Kernel()
        self.brain_start(brainfile, memoriesfile, aimlpath)
        self.nick = nick

    def brain_start(self, brainfile, memoriesfile, aimlpath):
        """Creates the brain file if needed and then loads it.
        Afterwards, the memories will be loaded so the bot gets her identity"""
        log.debug("CardboardAlice brain_start")

        if os.path.isfile(brainfile):
            # Brain is available, load it
            log.info("Found my brain, loading it now!")
            self.brain.bootstrap(brainFile=brainfile)
        else:
            # No brain file, so we create one.
            log.info("Didn't find my brain, generating a new one!")
            self.brain.bootstrap(learnFiles=aimlpath, commands="load aiml b")
            self.brain.saveBrain(brainfile)
        log.info("Brain loaded. Now setting all my memories!")
        yamlmemories = open(memoriesfile, 'r')
        memories = yaml.load(yamlmemories)
        for key, value in list(memories.items()):
            self.brain.setBotPredicate(key, value)

    def response(self, nick, body):
        """Generate a response using Alice AI subroutines"""
        log.debug("Generating a message through Alice AI")
        if body.startswith(self.nick + ": "):
            body = body.replace(self.nick + ": ", "", 1)

        body.replace(self.nick, "you")

        resp = self.brain.respond(body, nick)
        return resp
