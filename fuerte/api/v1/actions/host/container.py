#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Longgeek <longgeek@fuvism.com>

import os
import shutil
import subprocess

from fuerte.api.v1.utils import ceph_rbd_create


def create_container_extend_disk(inspect, username, user_path, cid):
    """ 创建容器时，在容器所在 docker 主机上执行额外的操作 """

    # 创建用户的基本目录
    if not os.path.exists(user_path):
        os.makedirs("%s/me" % user_path)
        os.makedirs("%s/learn" % user_path)
        os.makedirs("%s/containers" % user_path)

    # 如果用户的容器目录不存在，则创建
    if not os.path.exists("%s/containers/%s" % (user_path, cid)):
        os.makedirs("%s/containers/%s" % (user_path, cid))
        os.makedirs("%s/containers/%s/work" % (user_path, cid))

    try:
        # 找到容器的 overlay2 存储目录
        work = inspect["GraphDriver"]["Data"]["WorkDir"]
        upper = inspect["GraphDriver"]["Data"]["UpperDir"]

        # 删除原生的 overlay2 存储的 work 和 upper 目录
        shutil.rmtree(work)
        shutil.rmtree(upper)

        ceph_rbd_create(username, user_path, cid)
        if not os.path.exists("%s/containers/%s/diff" % (user_path, cid)):
            os.makedirs("%s/containers/%s/diff" % (user_path, cid))
        if not os.path.exists("%s/containers/%s/work" % (user_path, cid)):
            os.makedirs("%s/containers/%s/work" % (user_path, cid))

        # 禁止用户学习数据目录进行删除操作
        os.system("chattr +a -R %s/learn" % user_path)

        # 对共享存储中得目录软连接到 overlay2 存储目录中
        os.symlink("%s/containers/%s/work" % (user_path, cid), work)
        os.symlink("%s/containers/%s/diff" % (user_path, cid), upper)

        # #
        # # 使用 xfs quota 来限制容器存储空间
        # # 本方案已放弃，使用 ceph rbd 来指定块大小直接限制
        # #
        # if not os.path.exists("/etc/projects"):
        #     os.mknod("/etc/projects")
        # if not os.path.exists("/etc/projid"):
        #     os.mknod("/etc/projid")
        # fo = open("/etc/projects", "r+")
        # po = open("/etc/projid", "r+")
        # t_unix = int(time.mktime(datetime.datetime.now().timetuple()))
        # p_limit = "\n%s:%d" % (cid, t_unix)
        # d_limit = "\n%s:%s/containers/%s" % (t_unix, user_path, cid)
        # if "%s/containers/%s" % (user_path, cid) not in fo.read():
        #     fo.writelines(d_limit)
        # if cid not in po.read():
        #     po.writelines(p_limit)
        # fo.close()
        # po.close()
        # os.system("xfs_quota -x -c 'project -s %s' /storage" % cid)
        # os.system("xfs_quota -x -c 'limit -p bhard=5120m %s' /storage" % cid)
        # os.system("xfs_quota -x -c 'report /storage'")
    except Exception, e:
        return (-1, str(e), "")
    return (0, "", "")


def create_container_extend_net(inspect, user_path, cid):
    """ 启动容器后，限制容器的下载速率 """

    try:
        pid = inspect["State"]["Pid"]
        net_sandbox = inspect["NetworkSettings"]["SandboxKey"]

        if not os.path.exists("/var/run/netns"):
            os.mkdir("/var/run/netns")
        os.symlink(net_sandbox, "/var/run/netns/%s" % pid)

        # 获取主机虚拟网卡 ID
        pd = subprocess.Popen(
            ["ip netns exec %s ip link show eth1 | \
                                       head -n 1 | \
                                       awk -F: '{print $1}'" % pid],
            stdout=subprocess.PIPE,
            shell=True
        )
        veth_id = pd.stdout.read().strip()
        pd.stdout.close()

        # 获取主机虚拟网卡名称
        pn = subprocess.Popen(
            ["ip link | grep -e '%s:' | \
                     awk '{print $2}' | \
                     awk -F@ '{print $1}'" % veth_id],
            stdout=subprocess.PIPE,
            shell=True
        )
        veth_name = pn.stdout.read().strip()
        pn.stdout.close()

        # 删除生成的链接文件
        os.remove("/var/run/netns/%s" % pid)

        # 使用 TC 对主机商的虚拟网卡限制下载速率: 1mbit（100KB/s）
        pt = subprocess.Popen(
            ["tc qdisc add dev %s root tbf rate \
              1mbit latency 50ms burst 10000 mpu 64 mtu 15000" % veth_name],
            stdout=subprocess.PIPE,
            shell=True
        )
        pt.stdout.close()
    except Exception, e:
        return (-1, str(e), "")
    return (0, "", "")
