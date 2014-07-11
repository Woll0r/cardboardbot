#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

# Needed for reading the memories file
import yaml

# Needed for loading the brain files
import aiml
import os.path

log = logging.getLogger(__name__)

class CardboardBrain:
    def __init__(self, brainfile, memoriesfile, aimlpath):
        # Initialize Alice
        self.brain = aiml.Kernel()
        self.brain_start(brainfile, memoriesfile, aimlpath)

    def brain_start(self, brainfile, memoriesfile, aimlpath):
        """Creates the brain file if needed and then loads it.
        Afterwards, the memories will be loaded so the bot gets her identity"""
        if os.path.isfile(brainfile):
            # Brain is available, load it
            log.info("Found my brain, loading it now!")
            self.brain.bootstrap(brainFile = brainfile)
        else:
            # No brain file, so we create one.
            log.info("Didn't find my brain, generating a new one!")
            self.brain.bootstrap(learnFiles = aimlpath, commands = "load aiml b")
            self.brain.saveBrain(brainfile)
        log.info("Brain loaded. Now setting all my memories!")
        yamlmemories = file(memoriesfile, 'r')
        memories = yaml.load(yamlmemories)
        for k, v in memories.items():
            self.brain.setBotPredicate(k, v)
    
    def alicemessage(self, nick, body):
        """Generate a response using Alice AI subroutines"""
        log.debug("I don't know what %s is saying, so I'll let Alice respond for me!" % nick)
        if body.startswith(self.nick + ": "):
            body = body.replace(self.nick + ": ", "", 1)
    
        body.replace(self.nick, "you")

        resp = self.brain.respond(body, nick)
        return resp
