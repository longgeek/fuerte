#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Longgeek <longgeek@fuvism.com>

import requests
from fuerte.api.v1.config import URL, HEADERS


def inspect(cid):
    """ 获取容器详细信息 """

    r = requests.get(
        url=URL + "/containers/%s/json" % cid,
        headers=HEADERS
    )
    s = r.status_code
    if s != 200:
        return (s, r.text, "")
    return (s, "", r.json())
