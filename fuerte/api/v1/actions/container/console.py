#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Longgeek <longgeek@fuvism.com>

import hashlib
import inspect
import processes
import simplejson as json

from fuerte import redis_store
from fuerte.api.v1.utils import pack_requests
from fuerte.api.v1.config import URL
from fuerte.api.v1.config import HEADERS
from fuerte.api.v1.config import BASE_CMD
from fuerte.api.v1.config import CONSOLE_DOMAIN
from fuerte.api.v1.config import CONSOLE_PORT_BEG


def console(username, cid, cmd=None):
    """ 在容器中打入 Console 进程 """

    params = {
        "AttachStdout": False,
        "AttachStderr": False,
        "Tty": True,
    }

    port = None
    if cmd:
        s, m, r = processes.processes(username, cid, cmd)
        if s == 0:
            return (s, "", r)
        else:
            port = r
            params["Cmd"] = ["/bin/sh", "-c", BASE_CMD % (r, "False", cmd)]
    else:
        params["Cmd"] = [
            "/bin/sh",
            "-c",
            BASE_CMD % (CONSOLE_PORT_BEG, "True", "bash")
        ]
    # 创建一个 Exec 实例
    req = pack_requests(
        "POST",
        {
            "url": URL + "/containers/%s/exec" % cid,
            "headers": HEADERS,
            "data": json.dumps(params)
        }
    )
    status = req.status_code
    if status != 201:
        return (status, req.text, "")

    # 启动 Exec 实例
    r = pack_requests(
        "POST",
        {
            "url": URL + "/exec/%s/start" % req.json()["Id"],
            "headers": HEADERS,
            "data": json.dumps({"Tty": True, "Detach": True})
        }
    )
    s = r.status_code
    if s != 200:
        return (s, r.text, "")
    s1, m1, r1 = console_save(username, cid, cmd, port)
    if s1 != 0:
        return (s1, m1, "")
    return (s1, "", r1)


def console_md5(username, cid, cmd):
    """ 根据用户名、容器ID、命令生成唯一的 md5 url 地址 """
    random_str = username + cid + cmd
    hash_str = cid[0:12] + hashlib.md5(random_str).hexdigest()[0:12]
    return "http://%s.%s.%s" % (
        hash_str,
        username, CONSOLE_DOMAIN
    )


def console_save(username, cid, cmd=None, port=None):
    """ 保存用户的 Console 地址到 Redis 中。"""

    # 获取容器所在 nginx 网络的 IP 地址
    s, m, r = inspect.inspect(cid)
    if s != 200:
        return (s, m, "")
    cip = r["NetworkSettings"]["Networks"]["fuvism-nginx"]["IPAddress"]

    if cmd and port:
        console_url = console_md5(username, cid, cmd)
        console_addr = "http://%s:%s" % (cip, port)
        redis_store.set(console_url, console_addr)
        return (0, "", console_url)
    else:
        # 第一次创建容器后，默认在 redis 中保存 ssh、8000 地址
        r = []
        for c in ["ssh", "8000"]:
            console_url = "http://%s.%s.%s" % (
                c,
                username,
                CONSOLE_DOMAIN,
            )
            r.append(console_url)
            console_addr = "http://%s:%s" % (cip, CONSOLE_PORT_BEG)
            if c == "8000":
                console_addr = "http://%s:%s" % (cip, "8000")
            redis_store.set(console_url, console_addr)
        return (0, "", r)
