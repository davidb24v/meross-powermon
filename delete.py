# -*- coding: utf-8 -*-

import config


def go(opts):
    cfg = config.load()
    devices = list(cfg["devices"].keys())
    if opts.name in devices:
        cfg["devices"].pop(opts.name)
        config.save(cfg)
    else:
        sys.exit('error: Device "{}" not found'.format(opts.name))
