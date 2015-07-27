"""CardboardBot Markov chain brain"""

import logging
from pymarkovchain import MarkovChain

log = logging.getLogger(__name__)


class CardboardMarkov():
    """CardboardBot Markov chain brain"""

    def __init__(self, markovdb):
        log.debug("CardboardMarkov init")
        mc = MarkovChain(markovdb)

    def response(self, nick, body):
        """Respond to a message"""

        log.debug("CardboardMarkov response")

        mc.generateString()
