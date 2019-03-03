# -*- coding: utf-8 -*-

import subprocess
import requests
import base64
import subprocess
import time
import os
import sys

from iwlist import iwlist
import config
from utils import mangle

UPDOWN = "ip link set dev {} {}"
ASSOCIATE = "iwconfig {} ap {} essid {} key off"
URL = "http://10.10.10.1"

HEADERS = dict({"from": "",
                "messageId": "",
                "method": "GET",
                "namespace": "Appliance.System.All",
                "payloadVersion": "",
                "sign": "",
                "timestamp": ""})


def go(opts):
    config.exists(fail=True)
    rootcfg = config.load()
    cfg = config.load_user(rootcfg["user"])
    cfg.update(rootcfg)
    interface = cfg["interface"]

    print("Looking for Meross device...", end="")
    wifi_up(interface)

    try:
        attempts = 0
        while attempts < 300:
            print(".", end="")
            sys.stdout.flush()
            content = iwlist.scan()
            cells = iwlist.parse(content)
            for cell in cells:
                if cell["essid"].startswith("Meross_"):
                    print("\nFound {}".format(cell["essid"]))

                    associate(cell, interface)
                    add_ip(interface)

                    # Get initial device data
                    dev0 = get_device_data()
                    device = dict()
                    device[opts.name] = dev0["payload"]["all"]["system"]

                    # Setup server details
                    dev1 = set_server_details(cfg, opts)

                    # Setup wifi details
                    dev2 = set_wifi_details(cfg)

                    # Save device config
                    config.add_device(device, opts, cfg["user"])
                    typ = device[opts.name]["hardware"]["type"]
                    print("Added {} ({})".format(opts.name, typ))

                    # We're done
                    attempts = 999
                    break

            attempts += 1
            time.sleep(1)

    except subprocess.CalledProcessError:
        pass

    finally:
        # Remove the IP address from the interface
        del_ip(interface)
        wifi_down(interface)


def wifi_up(interface):
    cmd = UPDOWN.format(interface, "up")
    run(cmd)


def wifi_down(interface):
    cmd = UPDOWN.format(interface, "down")
    run(cmd)


def associate(cell, interface):
    cmd = ASSOCIATE.format(interface, cell["mac"], cell["essid"])
    run(cmd)


def add_ip(interface):
    cmd = "ip addr add 10.10.10.100/24 dev {}".format(interface)
    run(cmd)


def del_ip(interface):
    cmd = "ip addr del 10.10.10.100/24 dev {}".format(interface)
    run(cmd)


def send(url, data):
    r = requests.post(url, json=data)
    if r.status_code != 200:
        print("status: ", r.status_code)
        sys.exit("error sending request to device: {}".format(url))
    return r.json()


def get_device_data():
    headers = HEADERS.copy()
    payload = dict()
    data = dict({"header": headers,
                 "payload": payload})
    return send(URL + "/config/", data)


def set_server_details(cfg, opts):
    header = HEADERS.copy()
    header["method"] = "SET"
    header["namespace"] = "Appliance.Config.Key"
    header["payloadVersion"] = 1
    header["timestamp"] = 0
    key = mangle(opts.name)
    payload = dict({"key": {
                        "gateway": {
                            "host": cfg["mqtt"]["server"],
                            "port": cfg["mqtt"]["port"],
                            "secondHost": cfg["mqtt"]["server"],
                            "secondPort": cfg["mqtt"]["port"]
                        },
                        "key": key,
                        "userId": key
                   }})

    data = dict({"header": header,
                 "payload": payload})
    return send(URL + "/config/", data)


def set_wifi_details(cfg):
    header = HEADERS.copy()
    header["method"] = "SET"
    header["namespace"] = "Appliance.Config.Wifi"
    header["payloadVersion"] = 0
    header["timestamp"] = 0
    payload = dict({"wifi": {"bssid": "",
                             "channel": 1,
                             "cipher": 3,
                             "encryption": 6,
                             "password": cfg["password"],
                             "ssid": cfg["ssid"]}})
    data = dict({"header": header,
                 "payload": payload})
    return send(URL + "/config/", data)


def run(cmd):
    print("- " + cmd, end=" ")
    result = subprocess.run(cmd.split(), timeout=3)
    result.check_returncode()
    print("OK")
