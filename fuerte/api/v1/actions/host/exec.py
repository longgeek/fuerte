#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Longgeek <longgeek@fuvism.com>

import requests
import subprocess
import simplejson as json

from fuerte.api.v1.config import NODE_IP
from fuerte.api.v1.config import HEADERS
from fuerte.api.v1.actions.container import inspect


def execute(cid, cmds):
    """ 在容器所在 Docker 主机上执行命令 """

    # 获取容器的详细信息
    s_inspect, m_inspect, r_inspect = inspect.inspect(cid)
    if s_inspect != 200:
        return (s_inspect, m_inspect, r_inspect)

    # 判断容器是否在当前主机上
    node = r_inspect["Node"]['IP']

    if node == NODE_IP:
        return execute_extend(cid, cmds)
    else:
        params = {"action": "Extend:HostExecuteExtend",
                  "params": {"cid": cid, "cmds": cmds}}
        r = requests.post(url="http://%s:8000/api/v1" % node,
                          headers=HEADERS,
                          data=json.dumps(params))
        s = r.status_code
        if s != 200:
            return (s, r.text, "")
        return (s, "", r.json())


def execute_extend(cid, cmds):
    """ 执行命令代码体 """

    has_error = {}
    for cmd in cmds:
        p = subprocess.Popen([cmd],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             shell=True)
        out, err = p.communicate()
        if err:
            has_error = {"error": err}
            break
    if not has_error:
        return (0, "", "")
    return (1, has_error, "")
