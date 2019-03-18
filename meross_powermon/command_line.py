# -*- coding: utf-8 -*-

import argcomplete
import argparse
import base64
import sys
import os

from meross_powermon.version import VERSION
from meross_powermon import (config, delete, init, monitor, setup)


def devices(prefix, parsed_args, **kwargs):
    config.exists(fail=True)
    cfg = config.load()
    result = ["all"]
    result.extend(config.list_devices(cfg))
    if not prefix.startswith("~"):
        pre = ""
        pfx = prefix
    else:
        pre = "~"
        pfx = prefix.lstrip("~")

    return [pre + name for name in result if name.startswith(pfx)]


def just_devices(prefix, parsed_args, **kwargs):
    config.exists(fail=True)
    cfg = config.load()
    result = []
    result.extend(config.list_devices(cfg))
    return [name for name in result if name.startswith(prefix)]


def arguments(*args):
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
        mon_d.add_argument('name', help="Remove named device "
                           ).completer = just_devices
        # Monitor (normal user)
        subcommands["monitor"] = monitor
        mon_p = subparser.add_parser("monitor",
                                     description="Monitor device(s)")
        mon_p.add_argument("--delay", type=int, default=5,
                           help="Delay between polling device (default=5s)")
        mon_p.add_argument("--abserr", type=float, default=1000,
                           help="Absolute error tolerance in mW "
                                "(default: 1000)")
        mon_p.add_argument("--relerr", type=float, default=0.05,
                           help="Relative error tolerance "
                                "(default: 0.05)")
        mon_p.add_argument('name', nargs="*", default=["all"],
                           help="Example monitoring of named devices. "
                                "(Defalt: all devices)").completer = devices

    argcomplete.autocomplete(parser, always_complete_options=False)
    return (parser.parse_args(*args), subcommands)


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
        parser.add_argument('--port', type=int,
                            help="MQTT port (default: 8883)")
        parser.add_argument('--ca-cert', default=None,
                            help="Certificate for connecting to MQTT server")
    parser.add_argument('--show', action="store_true",
                        help="Show configuration data")
