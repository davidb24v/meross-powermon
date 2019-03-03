# -*- coding: utf-8 -*-

import argparse
import base64
import sys
import os

from version import VERSION
import config
import delete
import init
import monitor
import setup


def arguments():
    # Parser to store arguments
    parser = argparse.ArgumentParser(description="meross ({}) - A tool for "
                                                 "local use of Meross IoT "
                                                 "kit".format(VERSION))

    # Subcommands
    subparser = parser.add_subparsers(dest="subcommand")
    subcommands = dict()

    # Config command
    cfg_p = subparser.add_parser("config",
                                 description="Update configuration info")
    subcommands["config"] = config
    config_or_init_options(cfg_p, required=False)

    # Init command
    ini_p = subparser.add_parser("init",
                                 description="Create and store initial"
                                             "configuration")
    subcommands["init"] = init
    config_or_init_options(ini_p, required=True)

    if os.getuid() == 0:
        # Setup (only if root)
        subcommands["setup"] = setup
        set_p = subparser.add_parser("setup",
                                     description="Locate and configure a "
                                                 "Meross device")
        set_p.add_argument('--force', action="store_true",
                           help="Allow overwriting of existing device names")
        set_p.add_argument('name', help="Local name for Meross device")

    else:
        # Delete (normal user)
        subcommands["delete"] = delete
        mon_d = subparser.add_parser("delete",
                                     description="Delete named device")
        mon_d.add_argument('name', help="Remove named device ")
        # Monitor (normal user)
        subcommands["monitor"] = monitor
        mon_p = subparser.add_parser("monitor",
                                     description="Monitor device(s)")
        mon_p.add_argument('name', nargs="?", default="all",
                           help="Example monitoring of named devices. "
                                "(Defalt: all devices)")

    return (parser.parse_args(), subcommands)


def config_or_init_options(parser, required):
    if os.getuid() == 0:
        parser.add_argument('--user', required=required,
                            help="Which user's config to update")
        parser.add_argument('--ssid', required=required,
                            help='Name of your wifi access point.')
        parser.add_argument('--password', required=required,
                            help='Your wifi password. ')
        parser.add_argument('--interface', default="wlan0", metavar="IF",
                            help="Wifi device (default: wlan0)")
    else:
        parser.add_argument('--server', required=required,
                            help="MQTT server")
        parser.add_argument('--port', type=int, default=8883,
                            help="MQTT port (default: 8883)")
        parser.add_argument('--ca-cert', default=None,
                            help="Certificate for connecting to MQTT server")
    parser.add_argument('--show', action="store_true",
                        help="Show configuration data")
