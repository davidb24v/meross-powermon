# -*- coding: utf-8 -*-

import base64
import json
import time
import logging
from math import isclose

import meross_powermon.config as config
from meross_powermon.modified_device import Mss310
from meross_powermon.utils import mangle


def go(opts):
    log = logging.getLogger("meross_powerplug")
    log.setLevel(logging.WARNING)
    cfg = config.load()
    p = dict()
    p["domain"] = cfg["server"]
    p["port"] = cfg["port"]
    p["ca_cert"] = cfg["ca_cert"]

    all_devices = sorted(config.list_devices(cfg))
    devices = []
    for name in opts.name:
        if name == "all":
            devices.extend(all_devices)
            continue
        if name.startswith("~"):
            rm = name.lstrip("~")
            try:
                devices.remove(rm)
            except ValueError:
                print('unknown device: "{}"'.format(rm))
        else:
            devices.append(name)

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

    if len(plugs) == 1:
        devmon(plugs[0], delay=opts.delay,
               abserr=opts.abserr, relerr=opts.relerr)
    else:
        for p in plugs:
            dV, mA, mW = electricity(p)
            output(p._name, dV, mA, mW, ts=False)


def electricity(device):
    res = device.get_electricity()
    e = res["electricity"]
    dV = e["voltage"]
    mA = e["current"]
    mW = e["power"]
    return dV, mA, mW


def output(name, dV, mA, mW, ts=True):
    t = time.ctime() if ts else ""
    print("{:>16}  {:8.2f}V  {:8.2f}A  "
          "{:8.2f}W  {}".format(name, dV/10, mA/1000, mW/1000, t))


def devmon(device, delay=1, abserr=1000, relerr=0.05):
    dV0, mA0, mW0 = electricity(device)
    output(device._name, dV0, mA0, mW0)
    time.sleep(delay)
    while True:
        dV, mA, mW = electricity(device)
        if not isclose(mW, mW0, rel_tol=relerr, abs_tol=abserr):
            output(device._name, dV, mA, mW)
            dV0, mA0, mW0 = dV, mA, mW
        time.sleep(delay)
