#!/usr/bin/python

import pycurl, json, urllib
from errors import *
from logging import getLogger
from decorator import decorator
from StringIO import StringIO

LOGGER = getLogger()

class issue:
    def clear(self):
        self.key = None
        self.summary = None
        self.project = None
        self.description = None

    def __init__(self):
        self.clear()

    def __repr__(self):
        return "(%s) %s" % (self.key, self.summary)

    def parse(self, source):
        try:
            self.key = source["key"]
            self.summary = source["fields"]["summary"]
            self.description = source["fields"]["description"]
            self.project = source["fields"]["project"]["key"]
        except Exception, e:
            LOGGER.exception(e)
            self.clear()

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

    def __request(self, function, params=None, method=None):
        LOGGER.debug("Sending request to \"%s\" with parameters \"%s\"" % (function, params))
        buf = StringIO()
        self.c.setopt(pycurl.WRITEFUNCTION, buf.write)
        
        params = urllib.urlencode(params)
        get_params = ""
        if method:
            self.c.setopt(method, 1)
            self.c.setopt(pycurl.POSTFIELDS, urllib.urlencode(params))
        else:
            get_params = "?%s" % params

        self.c.setopt(pycurl.URL, "%s/%s%s" % (self.server_url, function, get_params))

        self.c.setopt(pycurl.VERBOSE, False)
        self.c.perform()

        result = buf.getvalue()
        buf.close()
        return result
        

    def _cache_issue(self, issue):
        LOGGER.debug("Caching issue %s" % issue)
        self.issues[issue.key] = issue

    def get_issue(self, key):
        LOGGER.debug("Retrieving issue %s" % key)
        i = issue()
        i.parse(json.loads(self.__request("issue/%s" % key)))
        self._cache_issue(i)
        return i
    
    def search_issues(self, jql, startAt=0, results=50):
        LOGGER.debug("Searching for issues by request: '%s'" % jql)
        j = json.loads(self.__request("search", {"jql": jql, "startAt": startAt, "maxResults": results}))
        
        result = []
        for ji in j["issues"]:
            i = issue()
            i.parse(ji)
            self._cache_issue(i)
            result.append(i)
        return result
