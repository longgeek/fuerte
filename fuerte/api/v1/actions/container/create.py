#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Longgeek <longgeek@fuvism.com>

import os
import inspect
import console
import network
import requests
import simplejson as json

from fuerte import app
from fuerte.api.v1.config import URL
from fuerte.api.v1.config import HEADERS
from fuerte.api.v1.config import NODE_IP
from fuerte.api.v1.config import NETWORK_BASES_NAME
from fuerte.api.v1.config import NETWORK_NGINX_NAME
from fuerte.api.v1.actions.host.container import create_container_extend


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
            "NetworkMode": NETWORK_BASES_NAME,
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

    # 如果用户的容器目录不存在，则创建
    if not cid:
        os.makedirs("%s/containers/%s" % (user_path, req.json()["Id"]))
        os.makedirs("%s/containers/%s/diff" % (user_path, req.json()["Id"]))
        os.makedirs("%s/containers/%s/work" % (user_path, req.json()["Id"]))
        cid = req.json()["Id"]

    # 判断容器是否在当前主机上
    node = r_inspect["Node"]['IP']
    if node == NODE_IP:
        s, m, r = create_container_extend(r_inspect, user_path, cid)
        if s != 0:
            return (s, m, "")
    else:
        params = {
            "action": "Host:CreateContainerExtend",
            "params": {
                "cid": cid,
                "inspect": r_inspect,
                "user_path": user_path
            }
        }
        e_req = requests.post(
            url="http://%s:8000/api/v1" % node,
            headers=HEADERS,
            data=json.dumps(params)
        )
        app.logger.debug(e_req)

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
