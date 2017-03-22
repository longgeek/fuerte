#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Longgeek <longgeek@fuvism.com>

from fuerte.api.v1.utils import pack_requests
from fuerte.api.v1.config import URL
from fuerte.api.v1.config import HEADERS


def inspect(cid):
    """ 获取容器详细信息 """

    kwargs = {
        "url": URL + "/containers/%s/json" % cid,
        "headers": HEADERS
    }
    r = pack_requests("GET", **kwargs)
    s = r.status_code
    if s != 200:
        return (s, r.text, "")
    return (s, "", r.json())
