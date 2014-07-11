#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys                         # Systems stuff
import logging                     # Logging
from optparse import OptionParser  # Parse commandline options

# Load the modules
from cardboardmodules import CardboardBot

log = logging.getLogger(__name__)
        
if __name__ == '__main__':
    import config
    
    # Setup the command line arguments.
    optp = OptionParser()

    # JID and password options.
    optp.add_option("-j", "--jid", dest="jid",
                    help="JID to use")
    optp.add_option("-p", "--password", dest="password",
                    help="password to use")
    optp.add_option("-n", "--nick", dest="nick",
                    help="Nick to use in channels.")
    optp.add_option("-c", "--channel", dest="channel",
                    help="Channel to work in.")

    opts, args = optp.parse_args()

    # Setup logging.
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(name)s %(message)s',
                        filename='cardboardbot.log',
                        filemode='w+')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)-8s %(name)s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    if opts.jid is None:
        try:
            opts.jid = config.jid
        except NameError:
            log.critical("I require a JID!")
            exit(1)
    else:
        config.jid = opts.jid
    if opts.password is None:
        try:
            opts.password = config.password
        except NameError:
            log.critical("I require a password!")
            exit(1)
    else:
        config.password = opts.password
    if opts.nick is None:
        try:
            opts.nick = config.nick
        except NameError:
            log.critical("I require a nick!")
            exit(1)
    else:
        config.nick = opts.nick
    if opts.channel is None:
        try:
            opts.channel = config.channel
        except NameError:
            log.critical("I require a channel!")
            exit(1)
    else:
        config.channel = opts.channel
    
    # Set up the bot and it's required XMPP things
    xmpp = CardboardBot(config)

    # Connect!
    if xmpp.connect():
        xmpp.process(block=True)
    else:
        log.critical("Unable to connect!")
