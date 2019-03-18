# -*- coding: utf-8 -*-

import pytest
import os
from pathlib import Path
import json

import meross_powermon.init as init
import meross_powermon.command_line as cmd
import meross_powermon.config as config


DUMMY_CONTENTS = dict({"server": "test",
                       "port": 1234,
                       "ca_cert": "cb.crt"
                       })


def test_no_cfg(tmpdir, config_path):
    args = "config --server test --port 1234 --ca-cert cb.crt"
    with tmpdir.as_cwd():
        with pytest.raises(SystemExit) as ex:
            opts, subcmds = cmd.arguments(args.split())
            subcmds[opts.subcommand].go(opts)
        assert "No configuration file, run 'meross init' first" in str(ex)


def test_update_config(tmpdir, config_path):
    args = "config --server s2 --port 4321 --ca-cert zz.zzz"
    config_path.write_text(json.dumps(DUMMY_CONTENTS) + "\n")
    o = json.loads(config_path.read_text())
    assert o["server"] == "test"
    assert o["port"] == 1234
    assert o["ca_cert"] == "cb.crt"
    with tmpdir.as_cwd():
        assert config_path.exists()
        opts, subcmds = cmd.arguments(args.split())
        subcmds[opts.subcommand].go(opts)
        o = json.loads(config_path.read_text())
        assert o["server"] == "s2"
        assert o["port"] == 4321
        assert o["ca_cert"] == "zz.zzz"


def test_show(tmpdir, config_path, capsys):
    args = "config --show"
    config_path.write_text(json.dumps(DUMMY_CONTENTS) + "\n")
    opts, subcmds = cmd.arguments(args.split())
    subcmds[opts.subcommand].go(opts)
    out, err = capsys.readouterr()
    assert '"server": "test"' in out
    assert '"port": 1234' in out
    assert '"ca_cert": "cb.crt"' in out


def test_user_config_files(config_path):
    expected = "/home/numpty/.config/meross_powermon/config.json"
    assert config.user_config_file("numpty") == expected
