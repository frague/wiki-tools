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

        self.pages = {}

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

    def _cache_page(self, page):
        LOGGER.debug("Caching page (%s): %s" % (page["id"], page["title"]))
        self.pages["%s|%s" % (page["space"], page["title"])] = page["id"]

    @connect_first
    def get_page_id(self, space, page_title):
        LOGGER.debug("Looking for page id for %s: %s" % (space, page_title))
        key = "%s|%s" % (space, page_title)
        if key in self.pages:
            return self.pages[key]
        page = self.get_page(space, page_title)
        return page["id"]

    @connect_first
    def get_page(self, space, page_name):
        LOGGER.debug("Retrieving page %s: \"%s\"" % (space, page_name))
        page = self.server.confluence1.getPage(self.token, space, page_name)
        self._cache_page(page)
        return page

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

    @connect_first
    def upload_attachment(self, page_id, file_name, content_type, contents):
        LOGGER.debug("Uploading attachment (%s): %s to page %s - %s bytes of data" % (content_type, file_name, page_id, len(contents)))
        attachment = {"fileName": file_name, "contentType": content_type}
        self.server.confluence1.addAttachment(self.token, page_id, attachment, xmlrpclib.Binary(contents))

    """@connect_first
    def upload_attachment(self, page_title, file_name, content_type, contents):
        LOGGER.debug("Uploading attachment (%s): %s to page %s" % (content_type, file_name, page_title))
        attachment = {"name": file_name, "mimeType": content_type, "file": xmlrpclib.Binary(contents)}
        self.server.confluence1.putAttachment(self.token, page_title, attachment)"""
