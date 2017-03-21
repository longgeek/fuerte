#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Longgeek <longgeek@fuvism.com>

import simplejson as json

from fuerte.api.v1.utils import pack_requests
from fuerte.api.v1.config import URL
from fuerte.api.v1.config import HEADERS


def connect(cid, network_name):
    """ 将容器连接到一个网络 """

    params = {"Container": cid}
    r = pack_requests(
        "POST",
        {
            "url": URL + "/networks/%s/connect" % network_name,
            "headers": HEADERS,
            "data": json.dumps(params)
        }
    )
    s = r.status_code
    if s != 200:
        return (s, r.text, "")
    return (s, "", "")
