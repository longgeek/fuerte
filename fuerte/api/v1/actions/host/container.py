#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Longgeek <longgeek@fuvism.com>

import os
import time
import shutil
import datetime


def create_container_extend(inspect, user_path, cid):
    """ 创建容器时，在容器所在 docker 主机上执行额外的操作 """

    # 使用共享存储的话，这一段代码不需要再这里执行
    # 如果用户的容器目录不存在，则创建
    if not os.path.exists("%s/containers/%s" % (user_path, cid)):
        os.makedirs("%s/containers/%s" % (user_path, cid))
        os.makedirs("%s/containers/%s/diff" % (user_path, cid))
        os.makedirs("%s/containers/%s/work" % (user_path, cid))

    try:

        # 找到容器的 overlay2 存储目录
        work = inspect["GraphDriver"]["Data"]["WorkDir"]
        upper = inspect["GraphDriver"]["Data"]["UpperDir"]
        # 删除原生的 overlay2 存储的 work 和 upper 目录
        shutil.rmtree(work)
        shutil.rmtree(upper)
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
        # os.system("xfs_quota -x -c 'report /storage'")
        return (0, "", "")
    except Exception, e:
        return (-1, str(e), "")
