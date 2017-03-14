#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Longgeek <longgeek@fuvism.com>

import os
import time
import shutil
import inspect
import console
import network
import datetime
import requests
import simplejson as json

from fuerte.api.v1.config import URL
from fuerte.api.v1.config import HEADERS
from fuerte.api.v1.config import NETWORK_NGINX_NAME


def create(username, image, cid=None):
    """ 创建容器 """

    user_path = "/storage/user_data/%s" % username

    # 在存储中创建用户学习存储目录
    if not os.path.exists(user_path):
        os.makedirs("%s/me" % user_path)
        os.makedirs("%s/learn" % user_path)
        os.makedirs("%s/containers" % user_path)

    # 禁止用户学习数据目录进行删除操作
    os.system("chattr +a -R %s/learn" % user_path)

    # 创建容器参数
    params = {
        "Tty": True,
        "Cmd": "bash",
        "Image": image,
        "OpenStdin": True,
        "AttachStdin": True,
        "HostConfig": {
            "Memory": 102400000,  # 100M
            "MemorySwap": -1,
            "NetworkMode": "fuvism-base",
            "Binds": [
                "/storage/.system:/storage/.system:ro",
                "%s/me:/storage/me:rw" % user_path,
                "%s/learn:/storage/learn:rw" % user_path,
            ]
        },
    }

    # 创建容器
    req = requests.post(
        url=URL + "/containers/create",
        headers=HEADERS,
        data=json.dumps(params)
    )

    status = req.status_code
    if status != 201:
        return (status, req.text, "")

    # 获取容器的详细信息
    s_inspect, m_inspect, r_inspect = inspect.inspect(req.json()["Id"])
    if s_inspect != 200:
        return (s_inspect, m_inspect, r_inspect)

    # 找到容器的 overlay2 存储目录
    work = r_inspect["GraphDriver"]["Data"]["WorkDir"]
    upper = r_inspect["GraphDriver"]["Data"]["UpperDir"]

    # 删除原生的 overlay2 存储的 work 和 upper 目录
    shutil.rmtree(work)
    shutil.rmtree(upper)

    # 如果用户的容器目录不存在，则创建
    if not cid:
        os.makedirs("%s/containers/%s" % (user_path, req.json()["Id"]))
        os.makedirs("%s/containers/%s/diff" % (user_path, req.json()["Id"]))
        os.makedirs("%s/containers/%s/work" % (user_path, req.json()["Id"]))
        cid = req.json()["Id"]

    # 对共享存储中得目录软连接到 overlay2 存储目录中
    os.symlink("%s/containers/%s/work" % (user_path, cid), work)
    os.symlink("%s/containers/%s/diff" % (user_path, cid), upper)

    # 限制容器存储空间
    if not os.path.exists("/etc/projects"):
        os.mknod("/etc/projects")
    if not os.path.exists("/etc/projid"):
        os.mknod("/etc/projid")

    fo = open("/etc/projects", "r+")
    po = open("/etc/projid", "r+")

    t_unix = int(time.mktime(datetime.datetime.now().timetuple()))
    p_limit = "\n%s:%d" % (cid, t_unix)
    d_limit = "\n%s:%s/containers/%s" % (t_unix, user_path, cid)

    if "%s/containers/%s" % (user_path, cid) not in fo.read():
        fo.writelines(d_limit)
    if cid not in po.read():
        po.writelines(p_limit)

    fo.close()
    po.close()

    os.system("xfs_quota -x -c 'project -s %s' /storage" % cid)
    os.system("xfs_quota -x -c 'limit -p bhard=10m %s' /storage" % cid)
    os.system("xfs_quota -x -c 'report /storage'")

    # 启动容器
    r = requests.post(
        url=URL + "/containers/%s/start" % req.json()["Id"],
        headers=HEADERS
    )

    s = r.status_code
    if s != 204:
        return (s, r.text, "")

    # 连接容器到 nginx 网络中
    s_net, m_net, r_net = network.connect(
        req.json()["Id"],
        NETWORK_NGINX_NAME
    )
    if s_net != 200:
        return (s_net, m_net, "")

    # 打入 ssh web 进程，开启 8000 域名访问
    s_exec, m_exec, r_exec = console.console(username, req.json()["Id"])
    if s_exec != 0:
        return (s_exec, m_exec, r_exec)
    else:
        return (s, "", req.json()["Id"])
