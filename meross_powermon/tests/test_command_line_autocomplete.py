# -*- coding: utf-8 -*-

import pytest
import os
from pathlib import Path
import json
import argparse

import meross_powermon.command_line as cmd


def test_devices(mocker):
    config_exists = mocker.patch("meross_powermon.config.exists")
    config_exists.return_value = True
    config_load = mocker.patch("meross_powermon.config.load")
    config_load.return_value = dict()
    config_list_devices = mocker.patch("meross_powermon.config.list_devices")
    config_list_devices.return_value = ["a_dev1", "b_dev2"]

    assert cmd.devices("a", None, dummy=0) == ["all", "a_dev1"]
    assert cmd.devices("b", None, dummy=0) == ["b_dev2"]
    assert cmd.devices("~a_", None, dummy=0) == ["~a_dev1"]

    assert cmd.just_devices("b", None, dummy=0) == ["b_dev2"]
