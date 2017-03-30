#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Longgeek <longgeek@fuvism.com>

import os
import requests
import simplejson as json

from fuerte.api.v1.config import NODE_IP
from fuerte.api.v1.config import TOKEN_HEADERS
from fuerte.api.v1.actions.container import inspect


def write_files(files, cid=None):
    """为 Docker 主机或容器里写入文件内

    :param dict files:
        e.g.: {"/etc/hosts": "",
               "/tmp/test.txt": "the test.txt default content."}
    :param str or None cid: The container uuid
        cid is str: 为容器里的文件写入内容
        cid is None: 为当前主机的文件写入内容
    """

    if cid:
        # 获取容器的详细信息
        s_inspect, m_inspect, r_inspect = inspect.inspect(cid)
        if s_inspect != 200:
            return (s_inspect, m_inspect, r_inspect)

        # 判断容器是否在当前主机上
        pid = r_inspect['State']['Pid']
        node = r_inspect["Node"]['IP']

        if node == NODE_IP:
            return write_files_extend(files, pid)
        else:
            params = {"action": "Extend:WriteFilesExtend",
                      "params": {"pid": pid, "files": files}}
            r = requests.post(url="http://%s:8000/api/v1" % node,
                              headers=TOKEN_HEADERS,
                              data=json.dumps(params))
            s = r.status_code
            if s != 200:
                return (s, r.text, "")
            return (s, "", r.json())
    else:
        return write_files_extend(files)


def write_files_extend(files, pid=None):
    """ 写入文件内容代码体 """

    for f in files:
        pid_f = f
        if pid:
            pid_f = "/proc/%s/root" % pid + f

        # 文件所在的路径
        fp = os.path.dirname(pid_f)
        if not os.path.exists(fp):
            os.makedirs(fp)

        # 写入数据到文件中
        fo = open(pid_f, "w")
        if not files[f]:
            fo.write("")
        else:
            fo.writelines(files[f].encode("utf-8"))
        fo.close()
    return (0, "", "")
