#!/usr/bin/python

import xmlrpclib
import SOAPpy

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
        return wp
        

class WikiSoapApi:
    def __init__(self, server_url):
        self.server_url = server_url
        self.soap = None
        self.token = None

    def connect(self, user, password):
        self.soap = SOAPpy.WSDL.Proxy(self.server_url)
        self.token = self.soap.login(user, password)

    @property
    def is_connected(self):
        return self.token is not None

    def get_page(self, space, page_name):
        if self.is_connected:
            return WikiPage.parse(self.soap.getPage(self.token, space, page_name))
        raise Exception("Not connected to wiki server")

    def update_page(self, page, minor_change=False):
        if self.is_connected:
            self.soap.updatePage(self.token, page, {"versionComment": "", "minorEdit": minor_change})
        raise Exception("Not connected to wiki server")


class WikiXmlrpcApi:
    def __init__(self, server_url):
        self.server_url = server_url
        self.server = None
        self.token = None

    def connect(self, user, password):
        self.server = xmlrpclib.ServerProxy(self.server_url)
        self.token = self.server.confluence1.login(user, password)
        if not self.is_connected:
            raise Exception("Connection to wiki failed")

    @property
    def is_connected(self):
        return self.token is not None

    def get_page(self, space, page_name):
        if self.is_connected:
            return self.server.confluence1.getPage(self.token, space, page_name)
        raise Exception("Not connected to wiki server")

    def update_page(self, page, minor_change=False):
        if self.is_connected:
            return self.server.confluence1.updatePage(self.token, page, {"versionComment": "", "minorEdit": str(minor_change)})
        raise Exception("Not connected to wiki server")
