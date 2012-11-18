#!/usr/bin/python

class JiraError(Exception):
    """ Base """

class NotConnectedError(JiraError):
    """ Trying to perform the operation not being connected """

class ConnectionFailedError(JiraError):
    """ When connection to jira server failed """

class NotFoundError(JiraError):
    """ When something cannot be found in place where supposed to be """
