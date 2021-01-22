import logging
from logging.handlers import TimedRotatingFileHandler
import os
import sys

import configparser
import coloredlogs
import pandas
import urllib3


def read_config(section, setting):
    """Read config.ini configuration file from project
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
    """Check if connection session to APIC exists

    Args:
        session (obj): Request session object for further API calls

    Returns:
        CLI / Log error message
    """
    if session is None:
        logger.warning("Connection session with APIC missing")
        print('Please log in first with "connect -u [username]"')
        sys.exit()
    else:
        pass


def pd_write_excel(filename, data, sheet_name):
    """Write pandas dataframe to Excel file

    Args:
        filename (str): filename or path file
        data (obj): pandas dataframe
        sheet_name (str): name for Excel worksheet
    """
    if os.path.exists(filename):
        write_mode = "a"
    else:
        write_mode = "w"
    with pandas.ExcelWriter(path=filename, mode=write_mode) as writer:
        data.to_excel(writer, index=False, sheet_name=sheet_name)


# Disable unverified HTTPS request warnings
# -> https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings
allow_unverified_https_request = read_config(
    section="security", setting="allow_unverified_https_request"
)
if allow_unverified_https_request == "true":
    urllib3.disable_warnings()

# Set log variables
log_file = read_config(section="logging", setting="log_file")
log_level = read_config(section="logging", setting="log_level")
log_rotation = read_config(section="logging", setting="log_rotation")
log_backup = read_config(section="logging", setting="log_backup")

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
coloredlogs.install(level=log_level, fmt="%(name)s %(levelname)s %(message)s")
