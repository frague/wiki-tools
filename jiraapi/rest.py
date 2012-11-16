#!/usr/bin/python

import pycurl, json
from errors import *
from logging import getLogger
from decorator import decorator
from StringIO import StringIO

LOGGER = getLogger()

class api:
    def __init_curl(self, login, password):
        self.c = pycurl.Curl()
        self.c.setopt(pycurl.NOSIGNAL, 1)
        self.c.setopt(pycurl.CONNECTTIMEOUT, 30)
        self.c.setopt(pycurl.HTTPHEADER, ["Content-Type: application/json"])
        self.c.setopt(pycurl.USERPWD, '%s:%s' % (login, password))

    def __init__(self, server_url, login, password):
        self.server_url = server_url
        self.__init_curl(login, password)
        self.issues = {}

    def request(self, function, params="", method=None):
        buf = StringIO()
        self.c.setopt(pycurl.URL, "%s/%s" % (self.server_url, function))
        self.c.setopt(pycurl.WRITEFUNCTION, buf.write)
        if method:
            self.c.setopt(method, 1)
        self.c.setopt(pycurl.VERBOSE, False)
        self.c.perform()

        result = buf.getvalue()
        buf.close()
        return result
        

    def _cache_issue(self, issue):
        LOGGER.debug("Caching issue (%s): %s" % (issue["key"], issue["fields"]["summary"]))
        self.issues[issue["fields"]["summary"]] = issue["key"]

    def get_issue(self, key):
        LOGGER.debug("Retrieving issue %s" % key)
        i = self.request("issue/%s" % key)
        issue = json.loads(i)
        #print json.dumps(i, indent=4)
        #print issue["fields"].keys()
        self._cache_issue(issue)
        return issue

