#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Longgeek <longgeek@fuvism.com>

import os
import shutil

from fuerte import redis_store
from fuerte.api.v1.utils import pack_requests
from fuerte.api.v1.config import URL
from fuerte.api.v1.config import CONSOLE_DOMAIN


def delete(username, cid, reset=False):
    """ 删除容器
    同时删除 Redis 中的 URL 地址、卸载用户容器存储、unmap rbd image
    """

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
        return (s, "", "")
    except Exception, e:
        return (-1, str(e), "")
