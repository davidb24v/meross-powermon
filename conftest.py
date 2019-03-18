from pathlib import Path
import sys

import pytest
import py
import tempfile

sys.path.insert(0, str(Path(".").resolve()))


@pytest.fixture(scope="function")
def as_root(mocker):
    """
    Ensure that os.getuid() return 0
    """
    getuid = mocker.patch("os.getuid")
    getuid.return_value = 0
    return


@pytest.fixture(scope="function")
def config_path(tmpdir, monkeypatch):
    """
    Generate a path to a config file in the current "tmpdir" and patch
    pathlib.Path.expanduser so it returns the path to the config file
    """
    import meross_powermon.config as config
    target = Path(tmpdir) / "config.json"
    config.CONFIG = target.as_posix()
    monkeypatch.setattr("pathlib.Path.expanduser", lambda x: target)
    return target
