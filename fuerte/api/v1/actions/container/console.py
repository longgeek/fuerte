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
from fuerte.api.v1.config import NETWORK_NGINX_NAME


def console(username, cid, cmds=None):
    """在容器中打入 Console 进程

    :param str username: Fuvism user name
    :param str cid: The container uuid
    :param list or None cmd:
        str: Console command(e.g., `ipython`, `python manager.py runserver`)
        None: Bash console
    """

    urls = {}
    port = None
    params = {"AttachStdout": False, "AttachStderr": False, "Tty": True}

    if cmds:
        for cmd in cmds:
            s, m, r = processes.processes(username, cid, cmd)
            if s == 1:
                port = r
                params["Cmd"] = ["/bin/sh", "-c", BASE_CMD % (r, "False", cmd)]
                s, m, r = _console_exec(username, cid, params)
                if s != 0:
                    return (s, m, r)
                s, m, r = _console_save(username, cid, cmd, port)
                if s != 0:
                    return (s, m, "")
                urls[cmd] = r
            elif s == 0:
                urls[cmd] = r
            else:
                return (s, m, r)
        return (0, "", urls)
    else:
        for i in True, False:
            port = CONSOLE_PORT_BEG
            if not i:
                port = int(CONSOLE_PORT_BEG) + 1
            params["Cmd"] = [
                "/bin/sh",
                "-c",
                BASE_CMD % (port, "%s" % i, "bash")
            ]
            s, m, r = _console_exec(username, cid, params)
            if s != 0:
                return (s, m, r)
        s, m, r = _console_save(username, cid)
        if s != 0:
            return (s, m, "")
        return (s, m, r)


def _console_exec(username, cid, params):
    # 创建一个 Exec 实例
    kwargs = {
        "url": URL + "/containers/%s/exec" % cid,
        "headers": HEADERS,
        "data": json.dumps(params)
    }
    req = pack_requests("POST", **kwargs)
    status = req.status_code
    if status != 201:
        return (status, req.text, "")

    # 启动 Exec 实例
    kwargs = {
        "url": URL + "/exec/%s/start" % req.json()["Id"],
        "headers": HEADERS,
        "data": json.dumps({"Tty": True, "Detach": True})
    }
    r = pack_requests("POST", **kwargs)
    s = r.status_code
    if s != 200:
        return (s, r.text, "")
    return (0, "", "")


def _console_md5(username, cid, cmd):
    """ 根据用户名、容器ID、命令生成唯一的 md5 url 地址 """

    random_str = username + cid + cmd
    hash_str = cid[0:12] + hashlib.md5(random_str).hexdigest()[0:12]
    return "http://%s.%s.%s" % (
        hash_str,
        username, CONSOLE_DOMAIN
    )


def _console_save(username, cid, cmd=None, port=None):
    """ 保存用户的 Console 地址到 Redis 中。"""

    # 获取容器所在 nginx 网络的 IP 地址
    s, m, r = inspect.inspect(cid)
    if s != 200:
        return (s, m, "")
    cip = r["NetworkSettings"]["Networks"][NETWORK_NGINX_NAME]["IPAddress"]

    if cmd and port:
        console_url = _console_md5(username, cid, cmd)
        console_addr = "http://%s:%s" % (cip, port)
        redis_store.set(console_url, console_addr)
        return (0, "", console_url)
    else:
        # 第一次创建容器后，默认在 redis 中保存 ssh、8000 地址
        r = {}
        for c in ["ssh", "bash", "8000"]:
            console_url = "http://%s.%s.%s" % (c, username, CONSOLE_DOMAIN)
            console_addr = "http://%s:%s" % (cip, CONSOLE_PORT_BEG)
            if c == "bash":
                console_url = _console_md5(username, cid, "bash")
                console_addr = "http://%s:%s" % (cip,
                                                 int(CONSOLE_PORT_BEG) + 1)
            if c == "8000":
                console_addr = "http://%s:%s" % (cip, "8000")
            r[c] = console_url
            redis_store.set(console_url, console_addr)
        return (0, "", r)
