#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Longgeek <longgeek@fuvism.com>

import redis
import requests
from fuerte.api.v1.config import URL, CONSOLE_DOMAIN


def delete(username, cid):
    """ 删除容器，同时删除 Redis 中的 URL 地址 """

    r = requests.delete(url=URL + "/containers/%s?force=true" % cid)
    s = r.status_code
    if s != 204:
        return (s, r.text, "")

    # 删除该用户相关的所有域名解析
    rconn = redis.Redis(host="127.0.0.1", port=6379, db=0)
    urls = rconn.keys("*.%s.%s" % (username, CONSOLE_DOMAIN))
    rconn.delete(*urls)
    return (s, "", "")
