# -*- coding: utf-8 -*-

import pytest
import json
import argparse
import sys

from meross_powermon import config
from meross_powermon import monitor
from meross_powermon import command_line as cmd

DUMMY_USER = dict({"server": "test",
                   "port": 1234,
                   "ca_cert": "cb.crt"
                   })

DUMMY_DEVICE = dict({"dev1": {
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


class Dummy(object):
    def __init__(self, x, y, z, **kwdargs):
        self._name = "<NAME>"
        self.n = 0
        pass

    def get_electricity(self):
        self.n += 1
        if self.n == 3:
            sys.exit("OK: End of test")
        return {"electricity": {
                    "voltage": 100*self.n,
                    "current": 200*self.n,
                    "power": 3000*self.n}
                }


@pytest.fixture(scope="function")
def devices(config_path, mocker):
    user_config_file = mocker.patch("meross_powermon.config.user_config_file")
    user_config_file.return_value = config_path.as_posix()
    config_path.write_text(json.dumps(DUMMY_USER) + "\n")
    opts = argparse.Namespace()
    config.add_device(DUMMY_DEVICE, opts, "nobody")
    o = json.loads(config_path.read_text())
    # Copy dev1 device to dev2 and dev3
    o["devices"]["dev2"] = o["devices"]["dev1"]
    o["devices"]["dev3"] = o["devices"]["dev1"]
    config_path.write_text(json.dumps(o) + "\n")
    return ["dev1", "dev2", "dev3"]


def test_monitor_selection(tmpdir, devices, capsys):
    monitor.Mss310 = Dummy
    monitor.hook_for_testing = sys.exit
    args = "monitor dev2 dev3"
    with tmpdir.as_cwd():
        opts, subcmds = cmd.arguments(args.split())
        opts.delay = 0.0
        subcmds[opts.subcommand].go(opts)
    out, err = capsys.readouterr()
    assert "<NAME>     10.00V      0.20A      3.00W" in out


def test_monitor_bad_device(tmpdir, devices, capsys):
    monitor.Mss310 = Dummy
    args = "monitor all ~dev4"
    with tmpdir.as_cwd():
        opts, subcmds = cmd.arguments(args.split())
        opts.delay = 0.0
        subcmds[opts.subcommand].go(opts)
    out, err = capsys.readouterr()
    assert 'unknown device: "dev4"' in out


def test_monitor_all(tmpdir, devices, capsys):
    monitor.Mss310 = Dummy
    args = "monitor all"
    with tmpdir.as_cwd():
        opts, subcmds = cmd.arguments(args.split())
        opts.delay = 0.0
        subcmds[opts.subcommand].go(opts)
    out, err = capsys.readouterr()
    assert "<NAME>     10.00V      0.20A      3.00W" in out


def test_monitor_one(tmpdir, devices, capsys):
    monitor.Mss310 = Dummy
    args = "monitor all ~dev2 ~dev3"
    with tmpdir.as_cwd():
        opts, subcmds = cmd.arguments(args.split())
        opts.delay = 0.0
        with pytest.raises(SystemExit) as ex:
            subcmds[opts.subcommand].go(opts)
        assert "OK: End of test" in str(ex)
    out, err = capsys.readouterr()
    assert "<NAME>     10.00V      0.20A      3.00W" in out
