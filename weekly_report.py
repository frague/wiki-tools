#!/usr/bin/python

import re
import yaml
from wikiapi import xmlrpc
from utils import *
from logger import make_custom_logger
from jinja2 import Environment, PackageLoader

def split_requirements(line):
    cols = re.split("</td><td[^>]*>", line)
    LOGGER.info("* %s" % cols[0])
    return "%s</td><td>%s" % (cols[0], cols[1])

if __name__ == "__main__":
    LOGGER = make_custom_logger()
    config = get_config()

    env = Environment(loader=PackageLoader("weekly_report", "templates"))
    template = env.get_template("weekly_report.html")

    wn = int(today.strftime("%U"))
    LOGGER.info("Weekly %s Report" % wn)

    wiki_api = xmlrpc.api(config["wiki_xmlrpc"])

    wiki_api.connect(config["wiki_login"], config["wiki_password"])
    LOGGER.info("Retrieving scope information")
    page = wiki_api.get_page("DEC", config["scope_page"])

    requirements = [split_requirements(match.group(1)) 
        for match in re.finditer("<tr><td[^>]*>(([^<]|<[^/]|</[^t]|</t[^r])*)</td></tr>", page["content"])]
    LOGGER.info("%s requirement(s) found" % len(requirements))

    title = "Week %s Status Report" % wn
    content = template.render(requirements=requirements)
    LOGGER.info("Saving new blog post: \"%s\"" % title)
    wiki_api.store_blogpost("DEC", title, content)

    LOGGER.info("Done")
