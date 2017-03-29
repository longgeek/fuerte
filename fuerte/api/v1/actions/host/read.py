#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Longgeek <longgeek@fuvism.com>

import os
import requests
import subprocess
import simplejson as json

from fuerte.api.v1.config import NODE_IP
from fuerte.api.v1.config import HEADERS
from fuerte.api.v1.actions.container import inspect


def read_files(files, cid=None):
    """在 Docker 主机或容器中读取文件内容

    :param dict files:
        e.g.: {"/etc/hosts": "",
               "/tmp/test.txt": "the test.txt default content."}
    :param str or None cid: The container uuid
        cid is str: 读取容器里的文件内容
        cid is None: 读取主机里的文件内容
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
            return read_files_extend(files, pid)
        else:
            params = {"action": "Extend:ReadFilesExtend",
                      "params": {"pid": pid, "files": files}}
            r = requests.post(url="http://%s:8000/api/v1" % node,
                              headers=HEADERS,
                              data=json.dumps(params))
            s = r.status_code
            if s != 200:
                return (s, r.text, "")
            return (s, "", r.json())
    else:
        return read_files_extend(files)


def read_files_extend(files, pid=None):
    """ 读取文件内容代码体 """

    content = {}
    for f in files:
        if pid:
            pid_f = "/proc/%s/root" % pid + f
        else:
            pid_f = f
        # 文件所在的路径
        fp = os.path.dirname(pid_f)
        if not os.path.exists(fp):
            os.makedirs(fp)

        # 如果文件不存在, 写入默认内容
        if not os.path.exists(pid_f):
            fo = open(pid_f, "w")
            if not (files[f]):
                fo.write("")
            else:
                fo.writelines(files[f].encode("utf-8"))
            fo.close()
            content[f] = files[f]
        else:
            # 获取文件的类型
            p = subprocess.Popen(["file %s" % pid_f],
                                 stdout=subprocess.PIPE,
                                 shell=True)
            data = p.stdout.read()
            p.stdout.close()

            # 判断文件是否为普通文本类型，并读取文件内容
            if "text" in data or "empty" in data:
                fo = open(pid_f)
                fc = fo.read()
                fo.close()

                try:
                    json.dumps(fc)
                except:
                    fc = fc.decode("utf-8", "replace")
                content[f] = fc
            else:
                content[f] = False
    return (0, "", content)
