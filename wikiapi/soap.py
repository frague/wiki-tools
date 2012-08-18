#!/usr/bin/python

import SOAPpy
from logging import getLogger
from errors import *

LOGGER = getLogger()

class WikiPage:
    def __init__(self):
        self.id = None
        self.space = None
        self.title = None
        self.content = None
        self.version = None

    def __repr__(self):
        return "WikiPage %s:\"%s\"" % (self.space, self.title)

    def as_dict(self):
        return {"id": self.id, "space": self.space, "title": self.title, "content": self.content, "version": self.version}
    
    @staticmethod
    def parse(page):
        wp = WikiPage()
        wp.id, wp.space, wp.title, wp.version, wp.content = page.id, page.space, page.title, page.version, page.content
        LOGGER.debug("Parsing page \"%s\"" % wp)
        return wp
        

class api:
    def __init__(self, server_url):
        LOGGER.debug("SOAP api initialization for %s" % server_url)
        self.server_url = server_url
        self.soap = None
        self.token = None

    def connect(self, user, password):
        LOGGER.debug("Logging in through SOAP api")
        self.soap = SOAPpy.WSDL.Proxy(self.server_url)
        self.token = self.soap.login(user, password)

    @property
    def is_connected(self):
        return self.token is not None

    def get_page(self, space, page_name):
        if self.is_connected:
            return WikiPage.parse(self.soap.getPage(self.token, space, page_name))
        raise NotConnectedError

    def update_page(self, page, minor_change=False):
        LOGGER.debug("Updating the page \"%s\"" % page)
        if self.is_connected:
            self.soap.updatePage(self.token, page, {"versionComment": "", "minorEdit": minor_change})
        raise NotConnectedError

