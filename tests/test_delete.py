# -*- coding: utf-8 -*-

import pytest
import os
from pathlib import Path
import json
import argparse

import meross_powermon.init as init
import meross_powermon.command_line as cmd
import meross_powermon.config as config
import meross_powermon.delete as delete
from meross_powermon.utils import mangle


DUMMY_CONTENTS = dict({"user": "test",
                       "ssid": "TVlTU0lE",
                       "password": "U0VDUkVU",
                       "interface": "MYWLAN"
                       })

DUMMY_USER = dict({"server": "test",
                   "port": 1234,
                   "ca_cert": "cb.crt"
                   })

DUMMY_DEVICE = dict({"aircon": {
                        "hardware": {
                            "type": "mss310",
                            "subType": "us",
                            "version": "2.0.0",
                            "chipType": "mt7682",
                            "uuid": "12341234123412341234123412341234",
                            "macAddress": "34:29:8f:13:c9:0a"
                        },
                        "firmware": {
                            "version": "2.1.7",
                            "compileTime": "2018/11/08 09:58:45 GMT +08:00",
                            "wifiMac": "12:34:56:12:34:56",
                            "innerIp": "",
                            "server": "",
                            "port": 0,
                            "userId": 0
                        },
                        "time": {
                            "timestamp": 14,
                            "timezone": "",
                            "timeRule": []
                        },
                        "online": {
                            "status": 2
                        }
                    }})


def test_delete_device(tmpdir, mocker, as_root, config_path):
    user_config_file = mocker.patch("meross_powermon.config.user_config_file")
    user_config_file.return_value = config_path.as_posix()
    opts = argparse.Namespace()
    opts.force = False
    config_path.write_text(json.dumps(DUMMY_USER) + "\n")
    config.add_device(DUMMY_DEVICE, opts, "nobody")
    o = json.loads(config_path.read_text())
    opts.name = "aircon"

    # delete the devices
    delete.go(opts)

    # try to delete non-existent device
    with pytest.raises(SystemExit) as ex:
        delete.go(opts)
    assert 'Device "aircon" not found' in str(ex)
