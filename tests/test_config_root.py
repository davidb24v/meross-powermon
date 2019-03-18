# -*- coding: utf-8 -*-

import pytest
import os
from pathlib import Path
import json
import argparse

from meross_powermon import init
from meross_powermon import command_line as cmd
from meross_powermon import config
from meross_powermon.utils import mangle
from tests.definitions import (DUMMY_CONTENTS, DUMMY_USER, DUMMY_DEVICE)


def test_no_root_cfg(tmpdir, as_root, config_path):
    args = "config --user test --ssid MYSSID --password SECRET"
    args += " --interface MYWLAN"
    with tmpdir.as_cwd():
        with pytest.raises(SystemExit) as ex:
            opts, subcmds = cmd.arguments(args.split())
            subcmds[opts.subcommand].go(opts)
        assert "No configuration file, run 'meross init' first" in str(ex)


def test_load_user_cfg(tmpdir, as_root, config_path):
    with tmpdir.as_cwd():
        with pytest.raises(SystemExit) as ex:
            config.load('_NO_SUCH_USER_')
        assert "No user configuration file" in str(ex)


def test_update_root_config(tmpdir, as_root, config_path):
    args = "config --user x --ssid SSID2 --password PWD2 --interface wlan1"
    config_path.write_text(json.dumps(DUMMY_CONTENTS) + "\n")
    o = json.loads(config_path.read_text())
    assert o["user"] == "test"
    with tmpdir.as_cwd():
        assert config_path.exists()
        opts, subcmds = cmd.arguments(args.split())
        subcmds[opts.subcommand].go(opts)
        o = json.loads(config_path.read_text())
        assert o["user"] == "x"
        assert o["interface"] == "wlan1"
        assert o["ssid"] == mangle("SSID2")
        assert o["password"] == mangle("PWD2")


def test_add_device(tmpdir, mocker, as_root, config_path):
    user_config_file = mocker.patch("meross_powermon.config.user_config_file")
    user_config_file.return_value = config_path.as_posix()
    opts = argparse.Namespace()
    opts.force = False
    config_path.write_text(json.dumps(DUMMY_USER) + "\n")
    config.add_device(DUMMY_DEVICE, opts, "nobody")
    o = json.loads(config_path.read_text())
    assert isinstance(o["devices"], dict)

    # Add it again, without --force
    with pytest.raises(SystemExit) as ex:
        config.add_device(DUMMY_DEVICE, opts, "nobody")
    assert "Unable to overwrite device unless you use --force" in str(ex)

    # Add it again, with --force
    opts.force = True
    config.add_device(DUMMY_DEVICE, opts, "nobody")

    # Get all devices
    all = config.list_devices(o)
    assert all == ["aircon"]


def test_connect(mocker, config_path, as_root, monkeypatch):
    user_config_file = mocker.patch("meross_powermon.config.user_config_file")
    user_config_file.return_value = config_path.as_posix()
    opts = argparse.Namespace()
    opts.force = False
    config_path.write_text(json.dumps(DUMMY_USER) + "\n")
    config.add_device(DUMMY_DEVICE, opts, "nobody")
    o = json.loads(config_path.read_text())
    monkeypatch.setattr("meross_powermon.config.Mss310",
                        lambda x, y, z, **kwdargs: None)
    config.connect("aircon")
