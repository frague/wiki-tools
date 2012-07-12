#!/usr/bin/python

import re
import yaml
from wikiapi import xmlrpc
from utils import *
from logger import get_logger
from jinja2 import Environment, PackageLoader

if __name__ == "__main__":
    LOGGER = get_logger(__name__)
    config = get_config()

    env = Environment(loader=PackageLoader("weekly_report", "templates"))
    template = env.get_template("weekly_report.html")

    wn = int(today.strftime("%U"))
    LOGGER.info("Weekly report for week %s" % wn)

    wiki_api = xmlrpc.api(config["wiki_xmlrpc"])

    wiki_api.connect(config["wiki_login"], config["wiki_password"])
    LOGGER.info("Retrieving scope information")
    page = wiki_api.get_page("CH", config["scope_page"])

    requirements = [match.group(1) for match in re.finditer("\{tr[^}]*\}\{td[^}]*\}([^}]*)\{td", page["content"])]
    LOGGER.info("%s requirement(s) found" % len(requirements))

