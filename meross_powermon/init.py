# -*- coding: utf-8 -*-

import os

from meross_powermon import config
from meross_powermon.utils import mangle


def go(opts):
    config.exists(fail=False)
    cfg = config.load()
    if os.getuid() == 0:
        # root
        opts.ssid = mangle(opts.ssid)
        opts.password = mangle(opts.password)
        config.root_update(cfg, opts)
        config.save(cfg)
    else:
        # Normal user mode
        config.update(cfg, opts)
        config.save(cfg)
