# -*- coding: utf-8 -*-

import base64
import json
import time
import logging

import config
from modified_device import Mss310
from utils import mangle


def go(opts):
    log = logging.getLogger("meross_powerplug")
    log.setLevel(logging.WARNING)
    cfg = config.load()
    p = dict()
    p["domain"] = cfg["mqtt"]["server"]
    p["port"] = cfg["mqtt"]["port"]
    p["ca_cert"] = cfg["mqtt"]["ca_cert"]

    devices = config.list_devices(cfg)
    if opts.name != "all" and opts.name in devices:
        devices = [opts.name]

    plugs = []
    for dev in devices:
        device = cfg["devices"][dev]
        key = mangle(dev)
        p["uuid"] = device["hardware"]["uuid"]
        p["devName"] = dev
        p["devType"] = device["hardware"]["type"]
        p["hdwareVersion"] = device["hardware"]["version"]
        p["fmwareVersion"] = device["firmware"]["version"]
        plugs.append(Mss310("token", key, None, **p))

    while True:
        for d in plugs:
            res = d.get_electricity()
            e = res["electricity"]
            print("{:>16}  {:8.2f}V  {:8.2f}A  "
                  "{:8.2f}W".format(d._name,
                                    e["voltage"]/10,
                                    e["current"]/1000,
                                    e["power"]/1000))
        time.sleep(5)
        print()
