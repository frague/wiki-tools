#!/usr/bin/python

from jiraapi import rest
from utils import *
from logger import make_custom_logger


if __name__ == "__main__":
    LOGGER = make_custom_logger()
    config = get_config()

    jira_api = rest.api(config["jira_rest"], config["wiki_login"], config["wiki_password"])

    issues = jira_api.search_issues("", results=2)

    print issues
