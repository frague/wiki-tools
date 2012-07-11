#!/usr/bin/python

import yaml
from wikiapi import xmlrpc
from utils import *
from logger import get_logger
from jinja2 import Environment, PackageLoader

if __name__ == "__main__":
    LOGGER = get_logger(__name__)
    config = get_config()

    env = Environment(loader=PackageLoader("cross_review", "templates"))
    template = env.get_template("reviewers.html")

    wn = int(today.strftime("%U"))
    LOGGER.info("Update for: %s, week %s" % (printable_date(today), wn))

    data = yaml.load(read_file(config["offset_file"])) or {"week": 0, "offset": 0}
    LOGGER.info("Current offset: %s" % data["offset"])
    if data["week"] != wn:
        data["week"] = wn
        data["offset"] += 1
        if (data["offset"] % l) == 0:
            data["offset"] += 1
        write_file(filename, yaml.dump(data))
        LOGGER.info("Offset updated")

    LOGGER.info("Building reviewers table")
    reviewers = []
    re = config["reviewers"]
    l = len(re)
    for i in range(0, l):
        reviewers.append({"reviewer": re[i], "reviewee": re[(i + data["offset"]) % l]})

    LOGGER.info("Publishing data on wiki")

    wiki_api = xmlrpc.api(config["wiki_xmlrpc"])

    wiki_api.connect(config["wiki_login"], config["wiki_password"])
    page = wiki_api.get_page("CH", "Code review")
    page["content"] = template.render(reviewers=reviewers, updated=printable_date(today), week=wn)
    wiki_api.update_page(page, True)

    LOGGER.info("Done")