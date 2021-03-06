#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""CardboardBot, a Jabber chatbot with a bunch of uses"""

import logging  # Logging
from argparse import ArgumentParser  # Parse commandline options

log = logging.getLogger(__name__)


def main():
    """CardboardBot main execution"""
    import config

    # Load the modules
    from cardboardmodules import CardboardBot

    # Setup the command line arguments.
    optp = ArgumentParser()

    # JID and password options.
    optp.add_argument("-j", "--jid", dest="jid",
                      help="JID to use")
    optp.add_argument("-p", "--password", dest="password",
                      help="Password to use")
    optp.add_argument("--use-ipv6", dest="use_ipv6", action="store_true",
                      help="Enable IPv6")
    optp.add_argument("--no-use-ipv6", "--no-ipv6", dest="use_ipv6",
                      action="store_false", help="Disable IPv6")
    optp.add_argument("-n", "--nick", dest="nick",
                      help="Nick to use in channels.")
    optp.add_argument("-c", "--channel", dest="channel",
                      help="Channel to work in.")
    optp.add_argument("-d", "--databasefile", dest="databasefile",
                      help="Databasefile to use")
    optp.add_argument("-m", "--memoriesfile", dest="memoriesfile",
                      help="Memoriesfile to use")
    optp.add_argument("-b", "--brainfile", dest="brainfile",
                      help="Brainfile to use")
    optp.add_argument("-a", "--aimlpath", dest="aimlpath",
                      help="Aimlpath to use")
    opts = optp.parse_args()

    # Setup logging.
    logformat = '%(levelname)-8s %(name)s %(message)s'
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s ' + logformat,
                        filename='cardboardbot.log',
                        filemode='w+')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter(logformat)
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    if opts.jid is None:
        try:
            opts.jid = config.jid
        except NameError:
            log.critical("I require a JID!")
            exit(1)
    if opts.password is None:
        try:
            opts.password = config.password
        except NameError:
            log.critical("I require a password!")
            exit(1)
    if opts.use_ipv6 is None:
        try:
            opts.use_ipv6 = config.use_ipv6
        except NameError:
            log.warning("use_ipv6 not specified! Disabling IPv6 support...")
            opts.use_ipv6 = False
    if opts.nick is None:
        try:
            opts.nick = config.nick
        except NameError:
            log.critical("I require a nick!")
            exit(1)
    if opts.channel is None:
        try:
            opts.channel = config.channel
        except NameError:
            log.critical("I require a channel!")
            exit(1)
    if opts.databasefile is None:
        try:
            opts.databasefile = config.databasefile
        except NameError:
            log.critical("I require a databasefile!")
            exit(1)
    if opts.brainfile is None:
        try:
            opts.brainfile = config.brainfile
        except NameError:
            log.warning("brainfile not defined! Using default value...")
            opts.brainfile = "cardboardbrain.brn"
    if opts.memoriesfile is None:
        try:
            opts.memoriesfile = config.memoriesfile
        except NameError:
            log.critical("I require a memoriesfile!")
            exit(1)
    if opts.aimlpath is None:
        try:
            opts.aimlpath = config.aimlpath
        except NameError:
            log.warning("aimlpath not defined! Using default value...")
            opts.aimlpath = "aiml/std-startup.xml"

    # Set up the bot and it's required XMPP things
    xmpp = CardboardBot.CardboardBot(opts.jid, opts.password,
                                     opts.nick, opts.channel,
                                     opts.use_ipv6, opts.brainfile,
                                     opts.memoriesfile, opts.aimlpath,
                                     opts.databasefile)

    # Respond to termination signals properly
    xmpp.use_signals()

    # Connect!
    if xmpp.connect():
        xmpp.process(block=True)
    else:
        log.critical("Unable to connect!")

if __name__ == '__main__':
    main()
