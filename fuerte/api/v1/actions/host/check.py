#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Longgeek <longgeek@fuvism.com>

import os
import requests
import simplejson as json

from fuerte.api.v1.config import NODE_IP
from fuerte.api.v1.config import TOKEN_HEADERS
from fuerte.api.v1.actions.container import inspect


def fd_check(cid, fds):
    """在容器所在 Docker 主机上检测文件、目录是否创建

    :param str cid: The container uuid
    :param list fds: 要检测的数据结构
        e.g.: [
            {"type": "dir", "name": "/some/dirname"},
            {"type": "file", "name": "/some/filename"}
        ]
    """

    # 获取容器的详细信息
    s_inspect, m_inspect, r_inspect = inspect.inspect(cid)
    if s_inspect != 200:
        return (s_inspect, m_inspect, r_inspect)

    # 判断容器是否在当前主机上
    pid = r_inspect["State"]["Pid"]
    node = r_inspect["Node"]["IP"]

    if node == NODE_IP:
        return fd_check_extend(cid, fds, pid)
    else:
        params = {"action": "Extend:HostFdCheckExtend",
                  "params": {"cid": cid, "fds": fds, "pid": pid}}
        r = requests.post(url="http://%s:8000/api/v1" % node,
                          headers=TOKEN_HEADERS,
                          data=json.dumps(params))
        s = r.status_code
        if s != 200:
            return (s, r.text, "")
        return (s, "", r.json())


def fd_check_extend(cid, fds, pid):
    """ 检测代码体 """

    try:
        result = {}
        for fd in fds:
            fd_path = "/proc/%s/root" % pid + fd["name"]
            if fd["type"] == "file":
                if os.path.exists(fd_path) and \
                   os.path.isfile(fd_path):
                    result[fd["name"]] = True
                else:
                    result[fd["name"]] = False
            else:
                if os.path.exists(fd_path) and \
                   os.path.isdir(fd_path):
                    result[fd["name"]] = True
                else:
                    result[fd["name"]] = False
        return (0, "", result)
    except Exception, e:
        return (1, str(e), "")
