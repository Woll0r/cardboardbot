#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""CardboardBot Markov chain database generator script"""

import logging
from argparse import ArgumentParser

log = logging.getLogger(__name__)


def main():
    import config
    from pymarkovchain import MarkovChain

    optp = ArgumentParser()

    optp.add_argument("-d", "--database", dest="database",
                      help="Where to store the database")
    optp.add_argument("-f", "--file", dest="file",
                      help="File source to use for generating the database")
    opts = optp.parse_args()

    # Setup logging.
    logformat = '%(levelname)-8s %(name)s %(message)s'
    logging.basicConfig(level=logging.INFO,
                        format=logformat)

    if opts.database is None:
        try:
            opts.database = config.markovbrainfile
        except NameError:
            log.critical("I require a brainfile to write into!")
            exit(1)
    if opts.file is None:
        log.critical("I require an imput file to learn from!")
        exit(1)

    mc = MarkovChain(opts.database)

    mc.learnFromFile(opts.file)

if __name__ == "__main__":
    main()
