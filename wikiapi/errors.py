#!/usr/bin/python

class WikiError(Exception):
    """ Base """

class NotConnectedError(WikiError):
    """ Trying to perform the operation not being connected """

class ConnectionFailedError(WikiError):
    """ When connection to wiki server failed """
