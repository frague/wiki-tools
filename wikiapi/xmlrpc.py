#!/usr/bin/python

import xmlrpclib
from logger import get_logger

LOGGER = get_logger(__name__)

class api:
    def __init__(self, server_url):
        self.server_url = server_url
        self.server = None
        self.token = None

    def connect(self, user, password):
        LOGGER.debug("Connecting to xmlrpc api")
        self.server = xmlrpclib.ServerProxy(self.server_url)
        self.token = self.server.confluence1.login(user, password)
        if not self.is_connected:
            raise Exception("Connection to wiki failed")

    @property
    def is_connected(self):
        return self.token is not None

    def get_page(self, space, page_name):
        LOGGER.debug("Retrieving page %s: \"%s\"" % (space, page_name))
        if self.is_connected:
            return self.server.confluence1.getPage(self.token, space, page_name)
        raise Exception("Not connected to wiki server")

    def update_page(self, page, minor_change=False):
        LOGGER.debug("Page update")
        if self.is_connected:
            return self.server.confluence1.updatePage(self.token, page, {"versionComment": "", "minorEdit": str(minor_change)})
        raise Exception("Not connected to wiki server")

    def store_blogpost(self, space, title, content):
        LOGGER.debug("Saving blogpost \"%s\"" % title)
        if self.is_connected:
            return self.server.confluence1.storeBlogEntry(self.token,
                {"space": space, "title": title, "content": content})