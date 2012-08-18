#!/usr/bin/python

import os
import yaml
import datetime
from logging import getLogger

LOGGER = getLogger()

# File methods
def read_file(file_name):
    result = ""
    if os.path.exists(file_name):
        rf = file(file_name, "r")
        result = rf.read()
        rf.close()
        LOGGER.debug("File \"%s\" read" % file_name)
    else:
        LOGGER.error("File \"%s\" reading FAILED" % file_name)
    return result

def write_file(file_name, contents):
    LOGGER.debug("Writing to file \"%s\"" % file_name)
    wf = file(file_name, "w")
    wf.write(contents)
    wf.close()

def get_config(config_file="config.yaml"):
    return yaml.load(read_file(config_file))



# Date & time methods
today = datetime.datetime.now()

def printable_date(d):
    return d.strftime("%B, %d (%A)")
