# -*- coding: utf-8 -*-

"""
Check that init functions correctly when run as normal user
"""

import pytest
import os
from pathlib import Path
import json

import meross_powermon.init as init
import meross_powermon.command_line as cmd
import meross_powermon.config as config


DUMMY_CONTENTS = dict({"server": "test",
                       "port": 1234,
                       "ca_cert": "ca.crt"
                       })


def test_first_run(tmpdir, config_path):
    assert not config_path.exists()
    args = "init --server test --port 1234 --ca-cert ca.crt"
    with tmpdir.as_cwd():
        opts, subcmds = cmd.arguments(args.split())
        subcmds[opts.subcommand].go(opts)
        o = json.loads(config_path.read_text())
        assert o["server"] == "test"
        assert o["port"] == 1234
        assert o["ca_cert"] == "ca.crt"


def test_update_config(tmpdir, config_path):
    args = "init --server s2 --port 4321 --ca-cert zz.zzz"
    config_path.write_text(json.dumps(DUMMY_CONTENTS) + "\n")
    with tmpdir.as_cwd():
        assert config_path.exists()
        opts, subcmds = cmd.arguments(args.split())
        subcmds[opts.subcommand].go(opts)
        o = json.loads(config_path.read_text())
        assert o["server"] == "s2"
        assert o["port"] == 4321
        assert o["ca_cert"] == "zz.zzz"
