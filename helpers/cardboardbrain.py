#!/usr/bin/env python
# -*- coding: utf-8 -*-

import aiml
import os.path
import yaml

brain = aiml.Kernel()

def brain_start():
    if os.path.isfile("standard.brn"):
        print "Found my brain, loading it now!"
        brain.bootstrap(brainFile = "standard.brn")
    else:
        print "Didn't find my brain, generating a new one!"
        brain.bootstrap(learnFiles = "aiml/std-startup.xml", commands = "load aiml b")
        brain.saveBrain("standard.brn")
    print "Brain loaded. Now setting all my memories!"
    memoryfile = file('personality.yaml', 'r')
    memories = yaml.load(memoryfile)
    for k, v in memories.items():
        brain.setBotPredicate(k, v)

brain_start()

questions = ["What is your name?", "Are you a boy or a girl?", "Where do you live?", "What is your favorite movie?"]

for question in questions:
    resp = brain.respond(question)
    print resp
