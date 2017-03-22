#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Longgeek <longgeek@fuvism.com>

from fuerte import redis_store
from fuerte.api.v1.utils import pack_requests
from fuerte.api.v1.config import URL
from fuerte.api.v1.config import CONSOLE_DOMAIN


def delete(username, cid):
    """ 删除容器，同时删除 Redis 中的 URL 地址 """

    kwargs = {"url": URL + "/containers/%s?force=true" % cid}
    r = pack_requests("DELETE", **kwargs)
    s = r.status_code
    if s != 204:
        return (s, r.text, "")

    # 删除该用户相关的所有域名解析
    urls = redis_store.keys("*.%s.%s" % (username, CONSOLE_DOMAIN))
    redis_store.delete(*urls)
    return (s, "", "")
