#!/usr/bin/python

import re
import yaml
from wikiapi import xmlrpc
from utils import *
from logging import getLogger
from jinja2 import Environment, PackageLoader

if __name__ == "__main__":
    LOGGER = getLogger()
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

    title = "Weekly status report (week %s)" % wn
    content =template.render(requirements=requirements)
    LOGGER.info("Saving new blog post: \"%s\"" % title)
    wiki_api.store_blogpost("CH", title, content)

    LOGGER.info("Done")
