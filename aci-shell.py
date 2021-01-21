#!/usr/bin/env python3
import argparse
import datetime
import os
import sys
import time

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


if __name__ == "__main__":
    application = ACIshell()
    application.default_to_shell = True
    application.precmd(app.aci.set_apic_url())
    application.cmdloop()
