#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Longgeek <longgeek@fuvism.com>

import re
import console

from fuerte.api.v1.actions.host import execute
from fuerte.api.v1.utils import pack_requests
from fuerte.api.v1.config import URL
from fuerte.api.v1.config import HEADERS
from fuerte.api.v1.config import CONSOLE_PORT_BEG


def processes(username, cid, cmd=None):
    """ 获取容器中所有的进程

    :param str username: Fuvism user name
    :param str cid: The container uuid
    :param str or None cmd: 指定 cmd 后, 会查询命令相应的进程
    :returns:
        status = 0 存在则返回 Url 地址,
        status = 1 不存在则返回一个可用端口.
    """

    kwargs = {
        "url": URL + "/containers/%s/top" % cid,
        "headers": HEADERS,
    }
    r = pack_requests("GET", **kwargs)
    s = r.status_code
    if s != 200:
        return (s, r.text, "")
    exist_ports = []
    exist_process = False
    if cmd:
        # 遍历所有进程，匹配是否有 cmd 的进程
        for p in r.json()["Processes"]:
            # 判断 webfront 的 http 服务器进程是否存在
            if "SimpleHTTPServer" in p[-1] and "bash -c pushd" in p[-1]:
                if cmd.startswith("webfront"):
                    # 判断 http 服务器的根目录是否一致
                    if p[-1].split(" ")[3] != cmd.split(" ")[-1]:
                        execute.execute(cid, username, ["kill -9 %s" % p[1]])
                    else:
                        exist_process = True
                        exist_ports.append(int(p[-1].split(" ")[-1]))
                        break
                else:
                    exist_ports.append(int(p[-1].split(" ")[-1]))
            if "butterfly.server.py" in p[-1] and "/bin/sh -c" not in p[-1]:
                # 拿到当前进程的具体命令
                process_cmd = p[-1].split("--cmd=")[-1]

                # 判断命令的进程是否已存在
                # 存在则退出 for 循环
                if cmd == process_cmd:
                    exist_process = True
                    break

                # 获取当前进程占用的 TCP 端口号
                search_group = re.search(r"--port=(\d+) --login", p[-1])
                if search_group:
                    exist_ports.append(int(search_group.group(1)))

        # 判断命令的进程是否存在
        # 存在则返回改命令的 MD5 Url 地址
        if exist_process:
            return (0, "", console._console_md5(username, cid, cmd))
        # 不存在返回一个可用的端口号
        else:
            exist_ports.sort()
            if not exist_ports:
                return (1, "", CONSOLE_PORT_BEG)
            return (1, "", exist_ports[-1] + 1)
    else:
        return (s, "", r.json())
