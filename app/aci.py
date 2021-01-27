import re
import sys

import getpass
import json
import pandas
import requests

import app.util


# Global variable for APIC connectivity
url = None


def set_apic_url():
    """Generate APIC API URL from user input"""
    global url
    url = "https://" + input("Enter APIC FQDN: ") + "/api/"


def apic_login(username):
    """Login to APIC and quire authentication toke for further API requests

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
        app.util.logger.info(
            "Successful APIC login with user " + user + " on url " + url
        )
        return session
    except requests.exceptions.HTTPError as error:
        app.util.logger.error("HTTP error: " + str(error))
        app.util.logger.error("Data reported by APIC: " + str(api_call.text))
        sys.exit()


def apic_logout(session):
    """Logout from APIC

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


def show_epg_all(session, filename):
    """Show all EPGs from all Tenants

    Args:
        session (obj): Authentication Session from APIC login
        filename (str): Filename or path to file for export
    """
    global url
    api_url = url + "node/class/fvAEPg.json"
    try:
        api_call = session.get(api_url, verify=False)
        app.util.logger.info("Getting all EPGs from ACI")
        api_call.raise_for_status()
        api_data = json.loads(api_call.text)
        regex_tn = r"uni/tn-(.*)/ap-"
        regex_ap = r"uni/tn-.*/ap-(.*)/epg-"
        data = []
        for imdata in api_data["imdata"]:
            try:
                attributes = imdata["fvAEPg"]["attributes"]
                dn = attributes["dn"]
                epg = attributes["name"]
                alias = attributes["nameAlias"]
                tenant = re.search(regex_tn, dn).group(1)
                ap = re.search(regex_ap, dn).group(1)
                data.append(
                    {
                        "Tenant": tenant,
                        "Application Profile": ap,
                        "EPG": epg,
                        "Alias": alias,
                    }
                )
            except AttributeError as error:
                app.util.logger.error("Regex attribute error: " + str(error))
                app.util.logger.error("Original string: " + dn)
        columns = ["Tenant", "Application Profile", "EPG", "Alias"]
        dataframe = pandas.DataFrame(data, columns=columns)
        sorted_dataframe = dataframe.sort_values(
            by=["Tenant", "Application Profile", "EPG"]
        )
        print(sorted_dataframe.to_string(index=False, justify="right", col_space=8))
        if filename != "":
            app.util.pd_write_excel(
                filename=filename, data=sorted_dataframe, sheet_name="EPG"
            )
    except requests.exceptions.HTTPError as error:
        app.util.logger.error("HTTP error: " + str(error))
        app.util.logger.error("Data reported by APIC: " + str(api_call.text))


def show_interface_status(session, pod_id, node_id, filename):
    """Show interface status for all interfaces on a switch

    Args:
        session : (obj) Authentication session from APIC login
        pod_id : (str) POD-ID of switch
        node_id : (str) Node-ID of switch
        filename (str): Filename for export
    """
    global url
    api_url = (
        url
        + "node/class/topology/pod-"
        + pod_id
        + "/node-"
        + node_id
        + "/l1PhysIf.json?&rsp-subtree=children"
        + "&rsp-subtree-class=ethpmPhysIf&order-by=l1PhysIf.id"
    )
    try:
        api_call = session.get(api_url, verify=False)
        app.util.logger.info("Getting interface status for node " + node_id)
        api_call.raise_for_status()
        api_data = json.loads(api_call.text)
        data = []
        for imdata in api_data["imdata"]:
            attributes = imdata["l1PhysIf"]["attributes"]
            interface_id = attributes["id"]
            descr = attributes["descr"]
            adminSt = attributes["adminSt"]
            for children in imdata["l1PhysIf"]["children"]:
                attributes = children["ethpmPhysIf"]["attributes"]
                operSt = attributes["operSt"]
                operSpeed = attributes["operSpeed"]
                operStQual = attributes["operStQual"]
                operDuplex = attributes["operDuplex"]
                bundleIndex = attributes["bundleIndex"]
            data.append(
                {
                    "Port": interface_id,
                    "Description": descr,
                    "Admin State": adminSt,
                    "Oper. State": operSt,
                    "Oper. Reason": operStQual,
                    "Duplex": operDuplex,
                    "Speed": operSpeed,
                    "Port-Channel": bundleIndex,
                }
            )
        columns = [
            "Port",
            "Description",
            "Port-Channel",
            "Admin State",
            "Oper. State",
            "Oper. Reason",
            "Speed",
            "Duplex",
        ]
        dataframe = pandas.DataFrame(data, columns=columns)
        print(dataframe.to_string(index=False, justify="right", col_space=8))
        if filename != "":
            sheet_name = "interface status_" + pod_id + "_" + node_id
            app.util.pd_write_excel(
                filename=filename, data=dataframe, sheet_name=sheet_name
            )
    except requests.exceptions.HTTPError as error:
        app.util.logger.error("HTTP error: " + str(error))
        app.util.logger.error("Data reported by APIC: " + str(api_call.text))


def show_interface_deployed_epg(session, pod_id, node_id, interface, filename):
    """Show deployed EPGs on a switch interface

    Args:
        session : (obj) Authentication session from APIC login
        pod_id : (str) POD-ID of switch
        node_id : (str) Node-ID of switch
        interface : (str) Interface on desired switch
        filename (str): Filename for export
    """
    global url
    api_url = (
        url
        + "node/mo/topology/pod-"
        + pod_id
        + "/node-"
        + node_id
        + "/sys/phys-["
        + interface
        + "].json?rsp-subtree-include"
        + "=full-deployment&target-node=all&target-path=l1EthIfToEPg"
    )
    try:
        api_call = session.get(api_url, verify=False)
        app.util.logger.info(
            "Getting interface information for node " + node_id + " port " + interface
        )
        api_call.raise_for_status()
        api_data = json.loads(api_call.text)
        data = []
        for imdata in api_data["imdata"]:
            attributes = imdata["l1PhysIf"]["attributes"]
            interface_id = attributes["id"]
            descr = attributes["descr"]
            try:
                for children in imdata["l1PhysIf"]["children"]:
                    pconsCtrlrDeployCtx = children["pconsCtrlrDeployCtx"]
                    for children in pconsCtrlrDeployCtx["children"]:
                        attributes = children["pconsResourceCtx"]["attributes"]
                        ctxDn = attributes["ctxDn"]
                        data.append(
                            {
                                "Node": node_id,
                                "Port": interface_id,
                                "Description": descr,
                                "Deployed EPGs": ctxDn,
                            }
                        )
            except Exception:
                app.util.logger.info("No child objects found.")
                print("No EPG deployed on this port")
                pass
        columns = ["Node", "Port", "Description", "Deployed EPGs"]
        dataframe = pandas.DataFrame(data, columns=columns)
        print(dataframe.to_string(index=False, justify="right", col_space=8))
        if filename != "":
            interface = interface.replace("/","_")
            sheet_name = "interface epg_" + pod_id + "_" + node_id + "_" + interface
            app.util.pd_write_excel(
                filename=filename, data=dataframe, sheet_name=sheet_name
            )
    except requests.exceptions.HTTPError as error:
        app.util.logger.error("HTTP error: " + str(error))
        app.util.logger.error("Data reported by APIC: " + str(api_call.text))