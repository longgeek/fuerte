#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Longgeek <longgeek@fuvism.com>

import os
import shutil
import requests
import simplejson as json

from fuerte import redis_store
from fuerte.api.v1.utils import pack_requests
from fuerte.api.v1.config import URL
from fuerte.api.v1.config import NODE_IP
from fuerte.api.v1.config import TOKEN_HEADERS
from fuerte.api.v1.config import CONSOLE_DOMAIN
from fuerte.api.v1.actions.container import inspect


def delete(username, cid, reset=False):
    """删除容器

    在容器所在主机上删除 Redis 中的 URL 地址, 卸载用户容器存储, unmap rbd image

    :param str username: Fuvism user name
    :param str cid: The container uuid
    :param bool reset:
        reset is true, clear container data in ceph rbd
    """

    # 获取容器的详细信息
    s_inspect, m_inspect, r_inspect = inspect.inspect(cid)
    if s_inspect != 200:
        return (s_inspect, m_inspect, r_inspect)

    # 判断容器是否在当前主机上
    node = r_inspect["Node"]["IP"]

    if node == NODE_IP:
        return delete_extend(username, cid, reset)
    else:
        params = {"action": "Extend:ContainerDeleteExtend",
                  "params": {"cid": cid, "reset": reset, "username": username}}
        r = requests.post(url="http://%s:8000/api/v1" % node,
                          headers=TOKEN_HEADERS,
                          data=json.dumps(params))
        s = r.status_code
        if s != 200:
            return (s, r.text, "")
        return (s, r.json()["message"], r.json()["data"])


def delete_extend(username, cid, reset):
    """ 删除代码体 """

    try:
        kwargs = {"url": URL + "/containers/%s?force=true" % cid}
        r = pack_requests("DELETE", **kwargs)
        s = r.status_code
        if s != 204:
            return (s, r.text, "")

        # 删除该用户相关的所有域名解析
        urls = redis_store.keys("*.%s.%s" % (username, CONSOLE_DOMAIN))
        if urls:
            redis_store.delete(*urls)

        # 获取所有挂载点
        fo = open("/proc/mounts", "r")
        all_mounts = fo.readlines()
        fo.close()

        # 找到 map 的设备号
        mount = "/storage/user_data/%s/containers/%s" % (username, cid)
        for line in all_mounts:
            if mount in line:
                map_device = line.split(" ")[0]
                break

        # 卸载容器存储
        os.system("umount %s" % mount)
        shutil.rmtree(mount)

        # unmap rbd 镜像
        os.system("rbd unmap %s" % map_device)

        # 重置用户容器数据
        if reset:
            os.system("rbd remove %s_containers_%s" % (username, cid))
        return (s, "Container %s deleted successfully" % cid, "")
    except Exception, e:
        return (-1, str(e), "")
