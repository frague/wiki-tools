#!/usr/bin/python

import xmlrpclib
from errors import *
from logging import getLogger
from decorator import decorator

LOGGER = getLogger()

@decorator
def connect_first(f, *args, **kws):
    if not args[0].is_connected():
        raise NotConnectedError()
    return f(*args, **kws)
        
class api:
    def __init__(self, server_url):
        self.server_url = server_url
        self.server = None
        self.token = None

    def connect(self, user, password):
        LOGGER.debug("Connecting to xmlrpc api")
        try:
            self.server = xmlrpclib.ServerProxy(self.server_url)
            self.token = self.server.confluence1.login(user, password)
        except Exception, e:
            raise ConnectionFailedError(e)

        if not self.is_connected:
            raise ConnectionFailedError()

    def is_connected(self):
        return self.token is not None

    @connect_first
    def get_page(self, space, page_name):
        LOGGER.debug("Retrieving page %s: \"%s\"" % (space, page_name))
        return self.server.confluence1.getPage(self.token, space, page_name)

    @connect_first
    def update_page(self, page, minor_change=False):
        LOGGER.debug("Page update")
        return self.server.confluence1.updatePage(self.token, page, 
                {"versionComment": "", "minorEdit": str(minor_change)})

    @connect_first
    def store_blogpost(self, space, title, content):
        LOGGER.debug("Saving blogpost \"%s\"" % title)
        return self.server.confluence1.storeBlogEntry(self.token,
                {"space": space, "title": title, "content": content})
