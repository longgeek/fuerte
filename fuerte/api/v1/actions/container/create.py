#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Longgeek <longgeek@fuvism.com>

import os
import inspect
import console
import network
import requests
import simplejson as json

from fuerte.api.v1.utils import pack_requests
from fuerte.api.v1.config import URL
from fuerte.api.v1.config import HEADERS
from fuerte.api.v1.config import NODE_IP
from fuerte.api.v1.config import NETWORK_BASES_NAME
from fuerte.api.v1.config import NETWORK_NGINX_NAME
from fuerte.api.v1.actions.host.container import create_container_extend_net
from fuerte.api.v1.actions.host.container import create_container_extend_disk


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
            "MemorySwap": 512000000,  # 512M
            "MemoryReservation": 80000000,  # 80M
            "NetworkMode": NETWORK_BASES_NAME,
            # 限制 CPU 最高使用率为 20%
            "CpuPeriod": 50000,
            "CpuQuota": 10000,
            "Ulimits": [
                {"Name": "nproc", "Hard": 512, "Soft": 400},
                {"Name": "nofile", "Hard": 1024, "Soft": 800},
            ],
            # 限制容器中最大进程数，可以有效防止 Fork 炸弹
            # https://blog.docker.com/2016/02/docker-engine-1-10-security/
            "PidsLimit": 512,
            "Binds": [
                "/storage/.system:/storage/.system:ro",
                "%s/me:/storage/me:rw" % user_path,
                "%s/learn:/storage/learn:rw" % user_path,
            ]
        },
    }

    kwargs = {
        "url": URL + "/containers/create",
        "headers": HEADERS,
        "data": json.dumps(params)
    }
    req = pack_requests("POST", **kwargs)
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

    # 在容器未启动之前，限制磁盘空间
    _limit_disk_quota(r_inspect, user_path, cid)

    # 启动容器
    kwargs = {
        "url": URL + "/containers/%s/start" % req.json()["Id"],
        "headers": HEADERS
    }
    r = pack_requests("POST", **kwargs)
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

    # 在容器启动后，限制容器下载速率
    _limit_network_bandwidth(user_path, cid)

    # 打入 ssh web 进程，开启 8000 域名访问
    s_exec, m_exec, r_exec = console.console(username, req.json()["Id"])
    if s_exec != 0:
        return (s_exec, m_exec, r_exec)
    else:
        return (s, "", req.json()["Id"])


def _limit_disk_quota(r_inspect, user_path, cid):
    """ 限制 Docker 容器磁盘使用空间 """

    # 判断容器是否在当前主机上
    node = r_inspect["Node"]['IP']
    if node == NODE_IP:
        s, m, r = create_container_extend_disk(r_inspect, user_path, cid)
        if s != 0:
            return (s, m, "")
    else:
        params = {
            "action": "Host:CreateContainerExtendDisk",
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
        e_status = e_req.status_code
        if e_status != 200:
            return (e_status, e_req.text, "")


def _limit_network_bandwidth(user_path, cid):
    """ 限制 Docker 网络的下载速率 """

    # 获取容器启动后的详细信息
    s_inspect, m_inspect, r_inspect = inspect.inspect(cid)
    if s_inspect != 200:
        return (s_inspect, m_inspect, r_inspect)

    # 判断容器是否在当前主机上
    node = r_inspect["Node"]['IP']
    if node == NODE_IP:
        s, m, r = create_container_extend_net(r_inspect, user_path, cid)
        if s != 0:
            return (s, m, "")
    else:
        params = {
            "action": "Host:CreateContainerExtendNet",
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
        e_status = e_req.status_code
        if e_status != 200:
            return (e_status, e_req.text, "")
