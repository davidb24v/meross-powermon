# -*- coding: utf-8 -*-

import pytest
import json
import argparse
import sys

from meross_powermon import (config, setup)
from meross_powermon import command_line as cmd
from meross_powermon.tests.definitions import (DUMMY_USER, DUMMY_DEVICE,
                                               DUMMY_CONTENTS)


@pytest.fixture(scope="function")
def prepare_setup(tmpdir, mocker, as_root, config_path):
    user_config_file = mocker.patch("meross_powermon.config.user_config_file")
    user_config_file.return_value = config_path.as_posix()
    config_path.write_text(json.dumps(DUMMY_USER) + "\n")
    opts = argparse.Namespace()
    opts.force = False
    config.add_device(DUMMY_DEVICE, opts, "nobody")
    cfg = json.loads(config_path.read_text())
    cfg.update(DUMMY_CONTENTS)
    config.save(cfg)
    _ = mocker.patch("meross_powermon.config.save")
    scan = mocker.patch("meross_powermon.setup.iwlist.scan")
    parse = mocker.patch("meross_powermon.setup.iwlist.parse")
    parse.return_value = [{"essid": "Meross_Dummy_Device",
                           "mac": "12:34:56:78:9a:bc:de"}]
    post = mocker.patch("meross_powermon.setup.requests.post",
                        side_effect=mocked_post)
    run = mocker.patch("meross_powermon.setup.subprocess.run",
                       side_effect=MockedSubprocessRun)
    return opts, cfg, scan, parse, post, run


class MockedPost():
    def __init__(self, stat, payload):
        self.status_code = stat
        self.payload = payload

    def json(self):
        return self.payload


def mocked_post(*args, **kwargs):
    ns = kwargs["json"]["header"]["namespace"]
    if ns == "Appliance.System.All":
        res = dict({"payload": {
                        "all": {
                            "system": DUMMY_DEVICE["aircon"]
                        }
                    }})
        return MockedPost(200, res)
    elif ns == "Appliance.Config.Key":
        return MockedPost(200, {})
    elif ns == "Appliance.Config.Wifi":
        return MockedPost(200, {})
    return MockedPost(404, None)


class MockedSubprocessRun():
    def __init__(self, *args, **kwargs):
        pass

    def check_returncode(self):
        pass


def test_setup_device(tmpdir, as_root, prepare_setup):
    opts, cfg, scan, parse, post, run = prepare_setup
    with tmpdir.as_cwd():
        opts.name = "test-device"
        setup.go(opts)
    assert post.call_count == 3


def test_setup_duplicate_device(tmpdir, as_root, prepare_setup):
    opts, cfg, scan, parse, post, run = prepare_setup
    with tmpdir.as_cwd():
        opts.name = "aircon"
        with pytest.raises(SystemExit) as ex:
            setup.go(opts)
        assert "Unable to overwrite device unless you use --force" in str(ex)


def test_setup_force_duplicate_device(tmpdir, as_root, prepare_setup, mocker):
    opts, cfg, scan, parse, post, run = prepare_setup
    opts.force = True
    with tmpdir.as_cwd():
        opts.name = "aircon"
        setup.go(opts)
    assert post.call_count == 3
    c = mocker.call
    run.assert_has_calls([c("ip link set dev MYWLAN up".split(), timeout=3),
                          c("iwconfig MYWLAN ap 12:34:56:78:9a:bc:de "
                            "essid Meross_Dummy_Device key off".split(),
                            timeout=3),
                          c("ip addr add 10.10.10.100/24 dev MYWLAN".split(),
                            timeout=3),
                          c("ip addr del 10.10.10.100/24 dev MYWLAN".split(),
                            timeout=3),
                          c("ip link set dev MYWLAN down".split(), timeout=3)])
