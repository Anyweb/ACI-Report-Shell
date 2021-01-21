import logging
from logging.handlers import TimedRotatingFileHandler
import os
import sys

import configparser
import coloredlogs
import urllib3


def read_config(section, setting):
    """ Read config.ini configuration file from project
        root directory

    Args:
        section (str): name of section
        setting (str): name of setting

    Returns:
        str: configuration parameter
    """
    parser = configparser.SafeConfigParser()
    parser.read("config.ini")
    config = parser.get(section, setting)
    return config


def check_session(session):
    """ Check if connection sessions exists

    Args:
        session : (obj) Request session object for further API calls
                        Can be empty

    Returns:
        Message if not connected to APIC
    """
    if session is None:
        logger.warning("Connection session with APIC missing")
        print('Please log in first with "connect -u [username]"')
        sys.exit()
    else:
        pass


# Disable unverified HTTPS request warnings
# -> https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings
ignore_https_cert = read_config(section="common", setting="ignore_https_certificate")
if ignore_https_cert == "true":
    urllib3.disable_warnings()

# Set log variables
logfile = "./logs/application.log"
log_file = logfile
log_rotation = "W1"
log_backup = 25

# Instantiate rotating log
log_handler = TimedRotatingFileHandler(
    filename=log_file, when=log_rotation, backupCount=log_backup
)
log_format = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(filename)s" " - %(message)s"
)
log_handler.setFormatter(log_format)
logger = logging.getLogger(__name__)
logger.addHandler(log_handler)
logger.setLevel(logging.INFO)

# Set parameters for coloredlogs output
coloredlogs.install(level="INFO", fmt="%(name)s %(levelname)s %(message)s")
