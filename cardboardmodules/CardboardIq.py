"""CardboardIq module for handling IQ requests related to XMPP"""

import logging
import sleekxmpp
import xml.etree.ElementTree


log = logging.getLogger(__name__)


class CardboardIq():
    """CardboardIq class for handling IQ requests related to XMPP"""

    muc_namespace = 'http://jabber.org/protocol/muc#admin'

    def __init__(self, connection):
        self.connection = connection

    def banlist(self):
        root_element = ElementTree.Element('{' + self.muc_namespace + '}query')
        item = ElementTree.SubElement(root_element, 'item')
        item.set('affiliation', 'outcast')
        iq = self.connection.create_iq('banlist', 'get', root_element)

        response = iq.send()
        items = response.findall('.//{' + self.muc_namespace + '}item')
        log.debug("Banlist contents: " + str(items))
        
        res = ""
        for item in items:
            if item.get('jid') is not None:
                res += item.get('jid') + ": " + str(item[0].text)
        
        if not res: return "No bans on record!"
        return res