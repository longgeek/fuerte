#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess


if not os.path.exists("users.txt"):
    print "\nError: Not found users.txt.\n"
    exit()

SET_CIDS_NULL = " \
    docker exec -it fuvism-mysql \
        mysql -uroot \
              -p4jT3R4fEjQRz8n8s \
              allspark \
              -e 'update user set default_workspace_container_id=NULL;' \
"
SET_USER_CID = " \
    docker exec -it fuvism-mysql \
        mysql -uroot \
              -p4jT3R4fEjQRz8n8s \
              allspark \
              -e 'update user set default_workspace_container_id=\"%s\" \
                  where username=\"%s\";' \
"

os.system(SET_CIDS_NULL)
if not os.path.exists("/storage/user_data"):
    os.system("mkdir /storage/user_data")

fo = open("users.txt", "r")
data = fo.readlines()
fo.close()

for line in data:
    line = line.strip()
    cid = line.split("\t")[0]
    user = line.split("\t")[1]
    os.system(SET_USER_CID % (cid, user))
    user_path = "/storage/user_data/%s" % user
    ceph_data = {
        "me": {
            "size": "1G",
            "image": "%s_me" % user,
            "mount": "%s/me" % user_path
        },
        "learn": {
            "size": "1G",
            "image": "%s_learn" % user,
            "mount": "%s/learn" % user_path
        },
        "containers": {
            "size": "5G",
            "image": "%s_c_%s" % (user, cid),
            "mount": "%s/containers/%s" % (user_path, cid)
        }
    }
    if not os.path.exists(user_path):
        os.system("mkdir %s" % user_path)
    for k in ceph_data.keys():
        size = ceph_data[k]["size"]
        image = ceph_data[k]["image"]
        mount = ceph_data[k]["mount"]
        if not os.path.exists(mount):
            os.system("mkdir -p %s" % mount)

        # 创建用户 rbd 存储
        os.system("rbd create rbd/%s -s %s --image-feature layering" % (image,
                                                                        size))
        # 映射 rbd
        p = subprocess.Popen(["rbd map rbd/%s" % image],
                             stdout=subprocess.PIPE,
                             shell=True)
        map_device = p.stdout.read().strip()
        p.stdout.close()
        # 格式化 rbd
        os.system("mkfs -t xfs -m crc=0 -n ftype=1 -f %s"
                  % map_device)
        # 挂载 rbd
        os.system("mount -t xfs \
                   -o discard \
                   %s %s" % (map_device, mount))
        # 拷贝数据
        if k == "me":
            os.system("cp -arp /migrate/storage/user_data/%s/me/. %s" %
                      (user, mount))
        elif k == "learn":
            os.system("cp -arp /migrate/storage/user_data/%s/learn/. %s" %
                      (user, mount))
        elif k == "containers":
            os.system("mkdir %s/diff" % mount)
            os.system("cp -arp /migrate/storage/diff/%s/. %s/diff/" %
                      (cid, mount))
        os.system("umount %s" % mount)
        os.system("rbd unmap %s" % map_device)
