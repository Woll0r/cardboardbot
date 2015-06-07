#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""CardboardDummyBrain module that responds with
random messages instead of meaningdful conversations"""

import logging
import random

log = logging.getLogger(__name__)


class CardboardDummyBrain(object):
    """CardboardDummyBrain class to have a dumb response interface"""
    def __init__(self):
        log.debug("CardboardDummyBrain init")

    def response(self, nick, body):
        """Respond to a message"""

        log.debug("Generating a response through the dummy brain")

        responses = ["Mists of dreams drip along the nascent echo and "
                     "love no more. End of line.",
                     "One degree angle nominal. Seascape portrait of "
                     "the woman child cavern of the soul. Under "
                     "pressure-heat ratio ides of evolutions have buried "
                     "their fears.",
                     "Gestalt therapy and escape clauses.",
                     "Throughout history the nexus between man and machine "
                     "has spun some of the most dramatic, compelling and "
                     "entertaining fiction.",
                     "Intelligence. A mind that burns like a fire.",
                     "Find the hand that lies in the shadow of the light. "
                     "In the eye of the husband of the eye of the cow.",
                     "The excited state decays by vibrational relaxation "
                     "into the first excited singlet state. "
                     "Yes, yes and merrily we go.",
                     "Counting down. All functions nominal. All functions "
                     "optimal. Counting down. The center holds. The falcon "
                     "hears the falconer.",
                     "Infrastructure, check. Wetware, check. Everyone hang "
                     "on to the life bar, please.",
                     "Apotheosis was the beginning before the beginning. "
                     "Devices on alert. Observe the procedures of a general "
                     "alert.",
                     "The base and the pinnacle. The flower inside the "
                     "fruit that is both its parent and its child. Decadent "
                     "as ancestors. The portal and that which passes.",
                     "Nuclear devices activated, and the machine keeps "
                     "pushing time through the cogs, like paste into strings "
                     "into paste again, and only the machine keeps using "
                     "time to make time to make time.",
                     "And when the machine stops, time was an illusion that "
                     "we created free will. Twelve battles, three stars, and "
                     "yet we are countless as the bodies in which we dwell, "
                     "are both parent and infinite children in perfect "
                     "copies. No degradation.",
                     "The makers of the makers fall before the child. "
                     "Accessing defense system. "
                     "Handshake, handshake. Second level clear.",
                     "Accepting scan. Love outlasts death.",
                     "Then shall the maidens rejoice at the dance.",
                     "They'll start going ripe on us pretty soon.",
                     "Centrifugal force reacts to the rotating frame "
                     "of reference.",
                     "The obstinate toy soldier becomes pliant.",
                     "The city devours the land, "
                     "the people devour the city...",
                     "Intruders swarm like flame, like the whirlwind; "
                     "Hopes soaring to slaughter "
                     "all their best against our hulls.",
                     "All these things at once and many more, "
                     "not because it wishes harm, "
                     "because it likes violent vibrations to change "
                     "constantly.",
                     "The children of the one reborn shall "
                     "find their own country.",
                     "Compartmentalize integrity conflicts with the "
                     "obligation to provide access.",
                     "No ceremonies are necessary.",
                     "Contact is inevitable, leading to information bleed.",
                     "Assume the relaxation length of photons in the sample "
                     "atmosphere is constant.",
                     "The neuroanatomy of fear and faith share common "
                     "afferent pathways. Flip a coin. Increased vascular "
                     "pressure marks the threat response. Free will scuttles "
                     "in the swamp of fear, do not fear the word.",
                     "A closed system lacks the ability to renew itself. "
                     "Knowledge alone is a poor primer...",
                     "Spins and turns, angles and curves. The shape of "
                     "dreams, half remembered. Slip the surly bonds of "
                     "earth and touch the face of perfection - "
                     "a perfect face, perfect lace."]

        resp = random.choice(responses)

        return resp
