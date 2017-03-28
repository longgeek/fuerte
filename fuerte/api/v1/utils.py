#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Longgeek <longgeek@fuvism.com>

import os
import rbd
import rados
import requests
import subprocess

from fuerte.api.v1.config import TLS
from fuerte.api.v1.config import TLS_CERTS
from fuerte.api.v1.config import CEPH_CONF
from requests.packages.urllib3.exceptions import SNIMissingWarning
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.packages.urllib3.exceptions import InsecurePlatformWarning


# Disable requests the warnings
requests.packages.urllib3.disable_warnings(SNIMissingWarning)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)


def pack_requests(method, **kwargs):
    """ Add a certificate for requests """

    if TLS == "true" or TLS == "True":
        kwargs["verify"] = False
        kwargs["cert"] = TLS_CERTS

    if method == "get" or method == "GET":
        return requests.get(**kwargs)
    elif method == "post" or method == "POST":
        return requests.post(**kwargs)
    elif method == "delete" or method == "DELETE":
        return requests.delete(**kwargs)


def ceph_rbd_create(username, user_path, cid, pool="rbd"):
    """ Create ceph rbd for the user

    Docs in http://docs.ceph.org.cn/rbd/librbdpy/
    """
    data = {
        "me": {
            "size": "1G",
            "image": "%s_me" % username,
            "mount": "%s/me" % user_path
        },
        "learn": {
            "size": "1G",
            "image": "%s_learn" % username,
            "mount": "%s/learn" % user_path
        },
        "containers": {
            "size": "5G",
            "image": "%s_containers_%s" % (username, cid),
            "mount": "%s/containers/%s" % (user_path, cid)
        }
    }

    # 使用 rbd，连接 Rados 并打开一个 IO 上下文
    with rados.Rados(conffile=CEPH_CONF) as cluster:
        with cluster.open_ioctx(pool) as ioctx:
            # 实例化 rbd 对象，用它来创建映像
            rbd_inst = rbd.RBD()
            rbd_all_images = rbd_inst.list(ioctx)

            # 检测 image 是否已创建
            for k in data.keys():
                size = data[k]["size"]
                image = data[k]["image"]
                mount = data[k]["mount"]
                if image not in rbd_all_images:
                    # rbd_inst.create(ioctx, image, size)
                    os.system("rbd create %s/%s -s %s --image-feature \
                               layering" % (pool, image, size))
                    p = subprocess.Popen(["rbd map %s/%s" % (pool, image)],
                                         stdout=subprocess.PIPE,
                                         shell=True)
                    map_device = p.stdout.read().strip()
                    p.stdout.close()
                    os.system("mkfs -t xfs -m crc=0 -n ftype=1 -f %s"
                              % map_device)
                    os.system("mount -t xfs \
                               -o rw,relatime,attr2,inode64,prjquota \
                               %s %s" % (map_device, mount))
                else:
                    # 获取所有的 rbd image map
                    m = subprocess.Popen(["rbd showmapped"],
                                         stdout=subprocess.PIPE,
                                         shell=True)
                    all_maps = m.stdout.read().strip()
                    m.stdout.close()

                    # 如果 rbd image 没有被 map，则 map
                    if image not in all_maps:
                        p = subprocess.Popen(["rbd map %s/%s" % (pool, image)],
                                             stdout=subprocess.PIPE,
                                             shell=True)
                        map_device = p.stdout.read().strip()
                        p.stdout.close()
                    else:  # 已经 map，则获取 map 到本地的设备
                        for line in all_maps.split("\n"):
                            if image in line:
                                map_device = line.strip().split(" ")[-1]
                                break

                    # 获取所有的挂载点
                    fo = open("/proc/mounts", "r")
                    all_mounts = fo.read()
                    fo.close()

                    # 如果 map 的设备没有挂载，则挂载
                    if map_device not in all_mounts:
                        os.system("mount -t xfs \
                                   -o rw,relatime,attr2,inode64,prjquota \
                                   %s %s" % (map_device, mount))
