#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""CardboardLinks module for handling links in messages"""

import logging
import urlparse

import requests
import re

log = logging.getLogger(__name__)


class CardboardLinks(object):
    """CardboardLinks class for handling links in messages"""
    # pylint: disable=no-self-use
    def __init__(self, database):
        log.debug("CardboardLinks init")
        self._db = database

    def get_page_title(self, match, timestamp, sender):
        """Extract the page title from a link"""
        from bs4 import BeautifulSoup

        try:
            # Set our user-agent
            headers = {'user-agent': 'cardboardbot'}

            # Get headers for the content linked
            thing = requests.head(match, timeout=5, headers=headers)

            domain = urlparse.urlparse(match).hostname.split(".")
            domain = ".".join(len(domain[-2]) < 4 and domain[-3:] or domain[-2:])

            if domain == "youtu.be":
                domain = "youtube.com"
            if domain == "deviantart.net":
                domain = "deviantart.com"
            if domain == "facdn.net":
                domain = "furaffinity.net"

            # If this isn't HTML, we don't want to know more
            if not 'html' in thing.headers['content-type']:
                log.debug("%s isn't HTML!", match)
                self._db.insert_in_link_table(timestamp, sender, match, match, domain)
                return None

            # If it is HTML, we fetch the title
            res = requests.get(match, timeout=5, headers=headers)
            soup = BeautifulSoup(res.text)
            title = soup.title.string.strip()
            log.debug(title)
            self._db.insert_in_link_table(timestamp, sender, match, title, domain)
            return title
        except requests.exceptions.RequestException as ex:
            log.debug("Error fetching url " + match + " : " + str(ex))

    def get_oembed_page_title(self, url, timestamp, sender):
        """Extract the page title from a link using the oembed method (DeviantArt)"""
        import json

        try:
            headers = {'user-agent': 'cardboardbot'}
            res = requests.get(url, timeout=5, headers=headers)

            domain = urlparse.urlparse(url).hostname.split(".")
            domain = ".".join(len(domain[-2]) < 4 and domain[-3:] or domain[-2:])

            if domain == "deviantart.net":
                domain = "deviantart.com"

            result = json.loads(res.text)
            log.debug(result)
            title = result['title'] + ' by ' + result['author_name']
            link = result['url']
            self._db.insert_in_link_table(timestamp, sender, link, title, domain)
            return title
        except requests.exceptions.RequestException as ex:
            log.error("error fetching url " + url + " : " + str(ex))

    def get_e621_title(self, url, timestamp, sender):
        """Extract the page title from a link to e621 using their API"""
        import json

        try:
            headers = {'user-agent': 'cardboardbot'}
            res = requests.get(url, timeout=5, headers=headers)

            domain = urlparse.urlparse(url).hostname.split(".")
            domain = ".".join(len(domain[-2]) < 4 and domain[-3:] or domain[-2:])

            result = json.loads(res.text)
            log.debug(result)

            title = '#' + result['id'] + ' ' + result['tags']
            link = 'https://e621.net/post/show/' + result['id']

            self._db.insert_in_link_table(timestamp, sender, link, title, domain)
            return title
        except requests.exceptions.RequestException as ex:
            log.error("error fetching url " + url + " : " + str(ex))

    def handle_url(self, timestamp, sender, body):
        """Handle URL's and get titles from the pages"""
        # pylint: disable=line-too-long
        urlregex = re.compile(
            r"((([A-Za-z]{3,9}:(?:\/\/)?)(?:[-;:&=\+\$,\w]+@)?[A-Za-z0-9.-]+|(?:www.|[-;:&=\+\$,\w]+@)[A-Za-z0-9.-]+)((?:\/[\+~%\/.\w_-]*)?\??(?:[-\+=&;%@.\w_]*)#?(?:[\w]*))?)")
        matches = urlregex.findall(body)
        matches = [x[0] for x in matches]
        matches = [self.imgur_filter(x) for x in matches]
        matches = [self.e621_filter(x) for x in matches]
        matches = [self.derpibooru_filter(x) for x in matches]
        matches = [self.deviantart_filter(x) for x in matches]
        if matches:
            log.debug("I think I see an URL! " + " / ".join(matches))
            results = []
            for match in matches:
                if 'backend.deviantart.com/oembed' in match:
                    title = self.get_oembed_page_title(match, timestamp, sender)
                elif 'e621.net' in match and 'json' in match:
                    title = self.get_e621_title(match, timestamp, sender)
                else:
                    title = self.get_page_title(match, timestamp, sender)

                if title:
                    results.append(title)

            if not len(results):
                # no results
                return False
            result = " / ".join(results).strip()
            return result

    def imgur_filter(self, link):
        """Convert Imgur image links into their full fledged counterparts"""
        imgurregex = re.compile(r'^http(s)?://i.imgur.com/([a-zA-Z0-9]*)\..*$')
        match = imgurregex.match(link)
        if match:
            replacement = 'http://imgur.com/' + match.group(2)
            log.debug("replacing " + link + " with " + replacement)
            return replacement
        return link

    def e621_filter(self, link):
        """Convert e621 image links into their full fledged counterparts"""
        # pylint: disable=line-too-long
        e621regex = re.compile(
            r'http(s)?://static([0-9]*).e621.net/data(/sample)?.*?((?:[a-z0-9][a-z0-9]*[a-z0-9][a-z0-9]+[a-z0-9]*))')
        match = e621regex.match(link)
        if match:
            replacement = 'https://e621.net/post/show.json?md5=' + match.group(4)
            log.debug("replacing " + link + " with " + replacement)
            return replacement
        return link

    def derpibooru_filter(self, link):
        """Convert derpibooru image links into their full fledged counterparts"""
        derpibooruregex = re.compile(
            r'http(s)?://derpicdn.net/img/view/([0-9]{4}/[0-9]{1,2}/[0-9]{1,2})/([0-9]+)')
        match = derpibooruregex.match(link)
        if match:
            replacement = 'https://derpibooru.org/' + match.group(3)
            log.debug("Replacing " + link + " with " + replacement)
            return replacement
        return link

    def deviantart_filter(self, link):
        """Convert DeviantArt image links into their full fledged counterparts"""
        # pylint: disable=line-too-long
        devartregex = re.compile(r'^http(s)?://\w+\.deviantart\.[\w/]+-(\w+)\.\w+$')
        match = devartregex.match(link)
        if match:
            replacement = 'http://backend.deviantart.com/oembed?url=http://www.deviantart.com/gallery/%23/' + match.group(2)
            log.debug("replacing " + link + " with " + replacement)
            return replacement
        return link
