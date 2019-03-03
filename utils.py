# -*- coding: utf-8 -*-

import base64


def mangle(s):
    return str(base64.b64encode(s.encode("utf-8")), "utf-8")
