#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Longgeek <longgeek@fuvism.com>

import os
import requests
import subprocess
import simplejson as json

from fuerte.api.v1.config import NODE_IP
from fuerte.api.v1.config import TOKEN_HEADERS
from fuerte.api.v1.actions.container import inspect


def execute(cid, username, cmds):
    """在容器所在 Docker 主机上执行命令

    :param str cid: The container uuid
    :param list cmds: List of commands to execute
    """

    # 获取容器的详细信息
    s_inspect, m_inspect, r_inspect = inspect.inspect(cid)
    if s_inspect != 200:
        return (s_inspect, m_inspect, r_inspect)

    # 判断容器是否在当前主机上
    node = r_inspect["Node"]['IP']

    if node == NODE_IP:
        return execute_extend(cid, username, cmds)
    else:
        params = {"action": "Extend:HostExecuteExtend",
                  "params": {"cid": cid, "cmds": cmds, "username": username}}
        r = requests.post(url="http://%s:8000/api/v1" % node,
                          headers=TOKEN_HEADERS,
                          data=json.dumps(params))
        s = r.status_code
        if s != 200:
            return (s, r.text, "")
        return (s, r.json()["message"], r.json()["data"])


def execute_extend(cid, username, cmds):
    """ 执行命令代码体 """

    has_error = {}
    for cmd in cmds:
        learn_path = "/storage/user_data/%s/learn" % username
        if learn_path in cmd:
            os.system("chattr -R -i -a %s" % learn_path)
        p = subprocess.Popen([cmd],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             shell=True)
        out, err = p.communicate()
        if learn_path in cmd:
            os.system("chattr -R -i +a %s" % learn_path)
        if err:
            has_error = {"error": err}
            break
    if not has_error:
        return (0, "", "")
    return (-1, has_error, "")
