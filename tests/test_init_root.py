# -*- coding: utf-8 -*-

"""
Check that init functions correctly when run as root
"""

import pytest
import os
from pathlib import Path
import json

import meross_powermon.init as init
import meross_powermon.command_line as cmd
from meross_powermon.utils import mangle


DUMMY_CONTENTS = dict({"user": "test",
                       "ssid": "TVlTU0lE",
                       "password": "U0VDUkVU",
                       "interface": "MYWLAN"
                       })


def test_first_run(tmpdir, as_root, config_path):
    assert not config_path.exists()
    args = "init --user test --ssid MYSSID --password SECRET"
    args += " --interface MYWLAN"
    with tmpdir.as_cwd():
        opts, subcmds = cmd.arguments(args.split())
        subcmds[opts.subcommand].go(opts)
        o = json.loads(config_path.read_text())
        assert o["user"] == "test"
        assert o["interface"] == "MYWLAN"
        assert o["ssid"] == mangle("MYSSID")
        assert o["password"] == mangle("SECRET")


def test_update_config(tmpdir, as_root, config_path):
    args = "init --user x --ssid SSID2 --password PWD2 --interface wlan1"
    config_path.write_text(json.dumps(DUMMY_CONTENTS) + "\n")
    with tmpdir.as_cwd():
        assert config_path.exists()
        opts, subcmds = cmd.arguments(args.split())
        subcmds[opts.subcommand].go(opts)
        o = json.loads(config_path.read_text())
        assert o["user"] == "x"
        assert o["interface"] == "wlan1"
        assert o["ssid"] == mangle("SSID2")
        assert o["password"] == mangle("PWD2")
