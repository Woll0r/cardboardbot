"""CardboardIq module for handling IQ requests related to XMPP"""

import logging
import xml.etree.cElementTree as ET

import sleekxmpp
from sleekxmpp.exceptions import IqError, IqTimeout

log = logging.getLogger(__name__)


class CardboardIq(object):
    """CardboardIq class for handling IQ requests related to XMPP"""

    muc_namespace = 'http://jabber.org/protocol/muc#admin'

    def __init__(self, connection):
        self.connection = connection

    def banlist(self):
        """Fetch the banlist and process it"""
        # Register namespace to an empty prefix
        ET.register_namespace('', self.muc_namespace)

        # Create the query elements
        root_element = ET.Element('{' + self.muc_namespace + '}query')
        item = ET.SubElement(root_element, 'item')
        item.set('affiliation', 'outcast')

        # Create IQ stanza
        iq = self.connection.create_iq(id='banlist', itype='get',
                                       payload=root_element,
                                       namespace=self.muc_namespace)

        # Get response and find elements inside
        try:
            response = iq.send()
            items = response.findall('.//{' + self.muc_namespace + '}item')
            log.debug("Banlist contents: " + str(items))

            res = ""
            for item in items:
                if item.get('jid') is not None:
                    res += "\n" + item.get('jid') + ": " + str(item[0].text)
            return res
        except IqError as iqe:
            log.warning('IqError happened! Error: ' + iqe.text)
            return iqe.text
        except IqTimeout as iqt:
            log.warning('IqTimeout happened!')
            return iqt.text

    def ban(self, jid, reason=None):
        """Ban a user"""
        ET.register_namespace('', self.muc_namespace)

        root_element = ET.Element('{' + self.muc_namespace + '}query')
        item = ET.SubElement(root_element, 'item')
        item.set('affiliation', 'outcast')
        item.set('jid', jid)
        if reason is not None:
            reasonelement = ET.SubElement(item, 'reason')
            reasonelement.text = reason

        iq = self.connection.create_iq(id='ban', itype='set',
                                       payload=root_element,
                                       namespace=self.muc_namespace)

        try:
            response = iq.send()
            log.debug('Ban success')
            return True
        except IqError as iqe:
            log.warning('IqError happened! Error: ' + iqe.text)
            return False
        except IqTimeout as iqt:
            log.warning('IqTimeout happened!')
            return False
