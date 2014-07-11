#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

import urlparse
import urllib
import requests
import re

log = logging.getLogger(__name__)

class CardboardLinks:

    def __init__(self, db):
        self.db = db

    def get_page_title(self, match, timestamp, sender):
        try:
            headers = { 'user-agent': 'cardboardbot' }
            res = requests.get(match, timeout=5, headers=headers)

            domain = urlparse.urlparse(match).hostname.split(".")
            domain = ".".join(len(domain[-2]) < 4 and domain[-3:] or domain[-2:])

            if domain == "youtu.be":
                domain = "youtube.com"
            if domain == "deviantart.net":
                domain = "deviantart.com"
            if domain == "facdn.net":
                domain = "furaffinity.net"
            
            if not 'html' in res.headers['content-type']:
                log.debug("%s isn't HTML!" % match)
                self.db.insert_in_link_table(timestamp, sender, match, match, domain)
                return None
            else:
                soup = BeautifulSoup(res.text)
                title = soup.title.string.strip()
                self.db.insert_in_link_table(timestamp, sender, match, title, domain)
                return title
        except Exception as e:
            log.debug("Error fetching url "+match+" : "+str(e))
            pass

    def get_oembed_page_title(self, url, timestamp, sender):
        import json
        try:
            headers = { 'user-agent': 'cardboardbot' }
            res = requests.get(url, timeout=5, headers=headers)
        
            domain = urlparse.urlparse(match).hostname.split(".")
            domain = ".".join(len(domain[-2]) < 4 and domain[-3:] or domain[-2:])
        
            if domain == "deviantart.net":
                domain = "deviantart.com"
        
            result = json.loads(res.text)
            log.debug(result)
            title = result['title'] + ' by ' +result['author_name']
            self.db.insert_in_link_table(timestamp, sender, url, title, domain)
            return title
        except Exception as e:
            log.error("error fetching url "+url+" : "+str(e))
    
    def handle_url(self, timestamp, sender, body):
        """Handle URL's and get titles from the pages"""
        urlregex = re.compile(r"((([A-Za-z]{3,9}:(?:\/\/)?)(?:[-;:&=\+\$,\w]+@)?[A-Za-z0-9.-]+|(?:www.|[-;:&=\+\$,\w]+@)[A-Za-z0-9.-]+)((?:\/[\+~%\/.\w_-]*)?\??(?:[-\+=&;%@.\w_]*)#?(?:[\w]*))?)")
        matches = urlregex.findall(body)
        matches = map(lambda x: x[0], matches)
        matches = map(self.imgur_filter, matches)
        matches = map(self.e621_filter, matches)
        matches = map(self.deviantart_filter, matches)
        if matches:
            log.debug("I think I see an URL! " + " / ".join(matches))
            results = []
            from bs4 import BeautifulSoup
            for match in matches:
                if 'oembed' in match:
                    title = self.get_oembed_title(match, timestamp, sender)
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
        if (match):
            replacement = 'http://imgur.com/'+match.group(2)
            log.debug("replacing "+link+" with "+replacement)
            return replacement
        return link

    def e621_filter(self, link):
        """Convert e621 image links into their full fledged counterparts"""
        e621regex = re.compile(r'http(s)?://static([0-9]*).e621.net/data(/sample)?.*?((?:[a-z0-9][a-z0-9]*[a-z0-9][a-z0-9]+[a-z0-9]*))')
        match = e621regex.match(link)
        if (match):
            replacement = 'https://e621.net/post/show?md5='+match.group(4)
            log.debug("replacing "+link+" with "+replacement)
            return replacement
        return link
    
    def deviantart_filter(self, link):
        devartregex = re.compile(r'^http(s)?://\w+\.deviantart\.[\w/]+-(\w+)\.\w+$')
        match = devartregex.match(link)
        if (match):
            replacement = 'http://backend.deviantart.com/oembed?url=http://www.deviantart.com/gallery/%23/'+match.group(2)
            log.debug("replacing "+link+" with "+replacement)
            return replacement
        return link