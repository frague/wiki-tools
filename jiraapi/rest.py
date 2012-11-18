#!/usr/bin/python

import pycurl, json, urllib
from errors import *
from logging import getLogger
from decorator import decorator
from StringIO import StringIO

LOGGER = getLogger()

class issue:
    """ Wrapper for json issue data for easier access """
    def clear(self):
        """ Clears objects properties """
        self.key = None
        self.summary = None
        self.project = None
        self.description = None
        self.status = None
        self.assignee = None

    def __init__(self):
        self.clear()

    def __repr__(self):
        return "(%s) %s [%s] - %s" % (self.key, self.summary, self.status, self.assignee)

    def parse(self, source):
        """ Parses source json and fills objects fields """
        try:
            self.key = source["key"]
            self.summary = source["fields"]["summary"]
            self.description = source["fields"]["description"]
            self.project = source["fields"]["project"]["key"]
            self.status = source["fields"]["status"]["name"]
            self.assignee = source["fields"]["assignee"]["name"]
        except Exception, e:
            LOGGER.exception(e)
            self.clear()

class worklog:
    def __init__(self):
        self.created = None
        self.reporter = None
        self.time_spent = None
        self.comment = None

    def __repr__(self):
        return "[%s] \"%s\", %s" % (self.time_spent, self.comment, self.reporter)

    def parse(self, source):
        self.created = source["created"]
        self.reporter = source["author"]["name"]
        self.time_spent = source["timeSpentSeconds"]
        self.comment = source["comment"]

class api:
    def __init_curl(self, login, password):
        """ REST api initialization & authentication data """
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
        """ Sends request to the REST api """
        LOGGER.debug("Sending request to \"%s\" with parameters \"%s\"" % (function, params))
        buf = StringIO()
        self.c.setopt(pycurl.WRITEFUNCTION, buf.write)
        
        get_params = ""
        if params:
            params = urllib.urlencode(params)
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
        """ Caches issue internally """
        LOGGER.debug("Caching issue %s" % issue)
        self.issues[issue.key] = issue

    def _parse_issue(self, json_loaded):
        """ New issue creation and caching """
        result = issue()
        result.parse(json_loaded)
        self._cache_issue(result)
        return result

    def _parse_issues(self, json_text):
        """ When multiple issues returned in result parses and caches each of them """
        j = json.loads(json_text)
        result = []
        for ji in j["issues"]:
            result.append(self._parse_issue(ji))
        return result

    def get_issue(self, key):
        """ Reads single issue """
        if key in self.issues.keys():
            return self.issues[key]
        LOGGER.debug("Retrieving issue %s" % key)
        return self._parse_issue(self.__request("issue/%s" % key))
    
    def jql_search(self, jql, startAt=0, results=50):
        """ Requests issues via jql query """
        LOGGER.debug("Searching for issues by request: '%s'" % jql)
        return self._parse_issues(self.__request("search", {"jql": jql, "startAt": startAt, "maxResults": results}))

    def filter_search(self, filter_id, startAt=0, results=50):
        """ Requests issues via predefined filter """
        LOGGER.debug("Searching for issues by filter: %s" % filter_id)
        filter = json.loads(self.__request("filter/%s" % int(filter_id)))
        if filter:
            LOGGER.debug("Filter id=%s found - '%s'" % (filter_id, filter["name"]))
            return self.jql_search(filter["jql"], startAt, results)
        raise NotFoundError("Unable to find filter with id=%s" % filter_id)

    def get_worklogs(self, issue_key):
        """ Requests all worklogs for the issue """
        LOGGER.debug("Requesting worklogs for issue %s" % issue_key)
        j = json.loads(self.__request("issue/%s/worklog" % issue_key))
        results = []
        for jt in j["worklogs"]:
            w = worklog()
            w.parse(jt)
            results.append(w)
        return results
