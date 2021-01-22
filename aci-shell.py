#!/usr/bin/env python3
import argparse

import cmd2

import app.util
import app.aci


session = None


class ACIshell(cmd2.Cmd):
    def __init__(self):
        super().__init__()
        self.intro = (
            "Welcome to the ACI shell \nPlease login" + ' with "connect -u [username]"'
        )
        self.prompt = ">>> "

    # -------------------------------------------------------------------------
    # Section for connection commands

    connect_parser = argparse.ArgumentParser()
    connect_parser.add_argument(
        "-u", "--username", dest="username", help="User for APIC login"
    )
    connect_args = connect_parser.parse_args()

    @cmd2.with_argparser(connect_parser)
    def do_connect(self, args):
        """ Connect to APIC """
        global session
        if args.username is not None:
            user = args.username
            session = app.aci.apic_login(user)
        else:
            print(
                "Error: Username arguement is required." 'Example: "connect -u admin"'
            )

    disconnect_parser = argparse.ArgumentParser()
    disconnect_args = disconnect_parser.parse_args()

    @cmd2.with_argparser(disconnect_parser)
    def do_disconnect(self, args):
        """ Disconnect from APIC """
        global session
        app.util.check_session(session)
        app.aci.apic_logout(session)

    # -------------------------------------------------------------------------
    # Section for show commands

    # show epg all
    show_epg_all_parser = argparse.ArgumentParser()
    show_epg_all_parser.add_argument(
        "-e", "--export", dest="filename", help="export report to file"
    )
    show_epg_all_args = show_epg_all_parser.parse_args()

    @cmd2.with_argparser(show_epg_all_parser)
    def do_show_epg_all(self, args):
        """ Show all EPGs from all tenants"""
        global session
        app.util.check_session(session)
        if args.filename is not None:
            report_dir = app.util.read_config(section="common", setting="report_dir")
            filename = report_dir + args.filename
            app.aci.show_epg_all(session=session, filename=filename)
        else:
            app.aci.show_epg_all(session=session, filename="")

    # show interface status
    show_interface_status_parser = argparse.ArgumentParser()
    show_interface_status_parser.add_argument(
        "-e", "--export", dest="filename", help="export report to file"
    )
    show_interface_status_parser.add_argument(
        "-p", "--pod-id", dest="pod_id", help="POD-ID"
    )
    show_interface_status_parser.add_argument(
        "-n", "--node-id", dest="node_id", help="Node-ID"
    )
    show_interface_status_args = show_interface_status_parser.parse_args()

    @cmd2.with_argparser(show_interface_status_parser)
    def do_show_interface_status(self, args):
        """ Show interface status for fabric node """
        global session
        app.util.check_session(session)
        if args.pod_id or args.node_id is not None:
            pod_id = args.pod_id
            node_id = args.node_id
            if args.filename is not None:
                report_dir = app.util.read_config(
                    section="common", setting="report_dir"
                )
                filename = report_dir + args.filename
                app.aci.show_interface_status(
                    session=session, pod_id=pod_id, node_id=node_id, filename=filename
                )
            else:
                app.aci.show_interface_status(
                    session=session, pod_id=pod_id, node_id=node_id, filename=""
                )
        else:
            print(
                "Error: pod-id and node-id arguements are required \n"
                'Example: "show_interface_status -p 1 -n 201"'
            )


if __name__ == "__main__":
    application = ACIshell()
    application.default_to_shell = True
    application.precmd(app.aci.set_apic_url())
    application.cmdloop()
