import collections
import os
import re
import sys
import time

import getpass
import json
import natsort
import pandas
import requests

import app.util


# Global variable for APIC connectivity
url = None


def set_apic_url():
    """ Generate APIC API URL from user input
    """
    global url
    url = "https://" + input("Enter APIC FQDN: ") + "/api/"


def apic_login(username):
    """ Login to APIC and quire authentication toke for further API requests

    Args:
        username (str): Username for APIC login

    Returns:
        obj: Request session object for further API requests
    """
    global url
    user = username
    try:
        check = requests.get(url, verify=False)
        check.status_code == 200
    except requests.exceptions.ConnectionError as error:
        app.util.logger.error("Connection error: " + str(error))
        sys.exit()
    try:
        print("APIC URL: " + url)
        password = getpass.getpass("Enter password for user " + user + ": ")
        raw_data = {"aaaUser": {"attributes": {"name": user, "pwd": password}}}
        api_data = json.dumps(raw_data)
        api_url = url + "aaaLogin.json"
        session = requests.session()
        api_call = session.post(api_url, data=api_data, verify=False)
        api_call.raise_for_status()
        app.util.logger.info("Successful APIC login with user " + user)
        return session
    except requests.exceptions.HTTPError as error:
        app.util.logger.error("HTTP error: " + str(error))
        app.util.logger.error("Data reported by APIC: " + str(api_call.text))
        sys.exit()


def apic_logout(session):
    """ Logout from APIC

    Args:
        session (obj): Authentication session from APIC login
    """
    global url
    try:
        check = requests.get(url, verify=False)
        check.status_code == 200
    except requests.exceptions.ConnectionError as error:
        app.util.logger.error("Connection error: " + str(error))
        sys.exit()
    try:
        print("APIC URL: " + url)
        api_url = url + "aaaLogout.json"
        api_call = session.post(api_url, verify=False)
        api_call.raise_for_status()
        if api_call.status_code == 200:
            app.util.logger.info("Successful APIC logout")
        else:
            print("Something went wrong")
    except requests.exceptions.HTTPError as error:
        app.util.logger.error("HTTP error: " + str(error))
        app.util.logger.error("Data reported by APIC: " + str(api_call.text))
        sys.exit()
