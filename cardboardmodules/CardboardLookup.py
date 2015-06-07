#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""CardboardLookup module for all things related to internet lookups"""

import logging
import json
import random

import requests
from cardboardmodules.CardboardMessage import CardboardMessage


log = logging.getLogger(__name__)


class CardboardLookup(object):
    """CardboardLookup class for all things related to internet lookups"""
    def __init__(self, links):
        log.debug("CardboardLookup init")
        self.links = links
        self.messager = CardboardMessage

    def fetch_from_url(self, url):
        """Fetch a page from the internet using the URL"""
        try:
            headers = {
                'user-agent': 'cardboardbot',
                'cache-control': 'no-cache'
            }
            log.debug("Fetching %s from the internet...", url)
            res = requests.get(url, headers=headers, timeout=10)
            return res.text
        except requests.exceptions.RequestException as ex:
            log.warning("Failed to fetch: %s", str(ex))
            return None

    def retrieve_specific_type(self, data, kind):
        """Retrieve a specific type from a dataset"""
        if isinstance(data, dict):
            return self.retrieve_specific_type_dict(data, kind)

        results = []
        for list_data in data:
            for child in self.retrieve_specific_type_dict(list_data, kind):
                results.append(child)

        return results

    def retrieve_specific_type_dict(self, data, kind):
        """Retrieve a specific type from a dictionary"""
        result = []

        if 'data' in data:
            for child in data['data']['children']:
                if child['kind'] == kind:
                    if not child['data']['is_self']:
                        result.append(child)

        return result

    def get_link(self, url, sender, timestamp):
        """Retrieve a random link from a Reddit URL"""
        json_data = self.fetch_from_url(url)
        if json_data is None:
            log.warning("Unable to retrieve json")
            return None, None, None  # Prevent errors!
        data = json.loads(json_data)

        links = self.retrieve_specific_type(data, 't3')

        if not links:
            log.warning("No links retrieved")
            return None, None, None

        link = random.choice(links)['data']

        self.links.handle_url(timestamp, sender, link['url'])

        return link['url'], link['title'], link['over_18']

    def build_message(self, url, title, nsfw):
        """Build a response with the link"""
        if url is None:
            return 'Could not look up your request :sweetiestare:', None
        plain = '{} [ {} ]'.format(title, url)
        html = '<a href="{}">{}</a>'.format(url, title)
        if nsfw:
            plain = ':nws: ' + plain + ' :nws:'
            html = ':nws: ' + html + ' :nws:'
        return plain, html

    def lookup(self, subreddit, sender, timestamp):
        """Get a random link from the specified subreddit"""
        link = "http://reddit.com/r/" + subreddit + ".json?count=100"
        url, title, nsfw = self.get_link(link, sender, timestamp)
        return self.build_message(url, title, nsfw)

    def clop(self, sender, timestamp):
        """Get a random link from /r/clopclop"""
        url, title, nsfw = self.get_link(
            "http://reddit.com/r/clopclop.json?count=100",
            sender, timestamp)
        return self.build_message(url, title, nsfw)

    def pony(self, sender, timestamp):
        """Get a random link from /r/mylittlepony"""
        url, title, nsfw = self.get_link(
            "http://reddit.com/r/mylittlepony.json?count=100",
            sender, timestamp)
        return self.build_message(url, title, nsfw)

    def ferret(self, sender, timestamp):
        """Get a random ferret"""
        url, title, nsfw = self.get_link(
            "http://reddit.com/r/ferret.json?count=100",
            sender, timestamp)
        return self.build_message(url, title, nsfw)
