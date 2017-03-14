#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Longgeek <longgeek@fuvism.com>

import os
import re
import time
import redis
import shutil
import hashlib
import datetime
import requests
import subprocess
import simplejson as json


DEFAULT_HTTP_HOST = "192.168.80.117"
DEFAULT_HTTP_PORT = "4000"
DEFAULT_CONSOLE_DOMAIN = "c.fuvism.com"
DEFAULT_CONSOLE_PORT_START = 43000
DEFAULT_CONSOLE_PORT_END = 44000
DEFAULT_NETWORK_BASE_NAME = "fuvism-base"
DEFAULT_NETWORK_NGINX_NAME = "fuvism-nginx"

url = "http://%s:%s" % (DEFAULT_HTTP_HOST, DEFAULT_HTTP_PORT)
headers = {"content-type": "application/json"}
base_cmd = "/storage/.system/.console/bin/butterfly.server.py \
     --unsecure \
     --host=0.0.0.0 \
     --port=%d \
     --login=%s \
     --cmd=%s"


def container_ps(**params):
    r = requests.Request("GET", url + "/containers/json")
    s = r.status_code
    if s != 200:
        return (s, r.text, "")
    return (s, "", r.json())


def container_inspect(cid):
    """ 获取容器详细信息 """

    r = requests.get(
        url=url + "/containers/%s/json" % cid,
        headers=headers
    )
    s = r.status_code
    if s != 200:
        return (s, r.text, "")
    return (s, "", r.json())


def container_network_connect(cid, network_name):
    """ 将容器连接到一个网络 """

    params = {"Container": cid}
    r = requests.post(
        url=url + "/networks/%s/connect" % network_name,
        headers=headers,
        data=json.dumps(params)
    )
    s = r.status_code
    if s != 200:
        return (s, r.text, "")
    return (s, "", "")


def container_create(username, image, cid=None):
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
        url=url + "/containers/create",
        headers=headers,
        data=json.dumps(params)
    )

    status = req.status_code
    if status != 201:
        return (status, req.text, "")

    # 获取容器的详细信息
    s_inspect, m_inspect, r_inspect = container_inspect(req.json()["Id"])
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
        url=url + "/containers/%s/start" % req.json()["Id"],
        headers=headers
    )

    s = r.status_code
    if s != 204:
        return (s, r.text, "")

    # 连接容器到 nginx 网络中
    s_net, m_net, r_net = container_network_connect(
        req.json()["Id"],
        DEFAULT_NETWORK_NGINX_NAME
    )
    if s_net != 200:
        return (s_net, m_net, "")

    # 打入 ssh web 进程，开启 8000 域名访问
    s_exec, m_exec, r_exec = container_console(username, req.json()["Id"])
    if s_exec != 200:
        return (s_exec, m_exec, r_exec)
    return (s, "", req.json()["Id"])


def container_processes(username, cid, cmd=None):
    """ 获取容器中所有的进程

    指定 cmd 后，会查询命令相应的进程:
    status = 0 存在则返回 Url 地址，
    status = 1 不存在则返回一个可用端口。
    """

    r = requests.get(
        url=url + "/containers/%s/top" % cid,
        headers=headers,
    )
    s = r.status_code
    if s != 200:
        return (s, r.text, "")
    exist_ports = []
    exist_process = False
    if cmd:
        # 遍历所有进程，匹配是否有 cmd 的进程
        for p in r.json()["Processes"]:
            if "butterfly.server.py" in p[-1] and "/bin/sh -c" not in p[-1]:
                # 拿到当前进程的具体命令
                process_cmd = p[-1].split("--cmd=")[-1]

                # 判断命令的进程是否已存在
                # 存在则退出 for 循环
                if cmd == process_cmd:
                    exist_process = True
                    break

                # 获取当前进程占用的 TCP 端口号
                search_group = re.search(r"--port=(\d+) --login", p[-1])
                if search_group:
                    exist_ports.append(int(search_group.group(1)))

        # 判断命令的进程是否存在
        # 存在则返回改命令的 MD5 Url 地址
        if exist_process:
            return (0, "", container_console_md5(username, cid, cmd))
        # 不存在返回一个可用的端口号
        else:
            exist_ports.sort()
            return (1, "", exist_ports[-1] + 1)
    else:
        return (s, "", r.json())


def container_exec(cid, cmds, wait=False):
    """ 在容器中执行命令

    cmds is LIST
    wait = True  命令将在前台执行，会等待命令执行完成
    wait = False 命令将在后台执行，不等待命令执行完成
    """

    if type(cmds) != list:
        return (-1, "cmds needs to be a list type parameter", "")

    if wait:
        results = []
        params = {
            "AttachStdin": False,
            "AttachStdout": True,
            "AttachStderr": True,
            "Tty": False,
        }
        for c in cmds:
            params["Cmd"] = ["/bin/sh", "-c", c]
            r = requests.post(
                url=url + "/containers/%s/exec" % cid,
                headers=headers,
                data=json.dumps(params)
            )
            s = r.status_code
            if s != 201:
                return (s, r.text, "")

            r = requests.post(
                url=url + "/exec/%s/start" % r.json()["Id"],
                headers=headers,
                data=json.dumps({"Tty": False, "Detach": False})
            )
            s = r.status_code
            results.append(r.text)
            if s != 200:
                return (s, r.text, "")
        return (0, "", results)
    else:
        params = {
            "AttachStdout": False,
            "AttachStderr": False,
            "Tty": True,
        }
        for c in cmds:
            params["Cmd"] = ["/bin/sh", "-c", c]
            r = requests.post(
                url=url + "/containers/%s/exec" % cid,
                headers=headers,
                data=json.dumps(params)
            )
            s = r.status_code
            if s != 201:
                return (s, r.text, "")

            r = requests.post(
                url=url + "/exec/%s/start" % r.json()["Id"],
                headers=headers,
                data=json.dumps({"Tty": True, "Detach": True})
            )
            s = r.status_code
            if s != 200:
                return (s, r.text, "")
        return (0, "", "")


def container_console(username, cid, cmd=None):
    """ 在容器中打入 Console 进程 """

    params = {
        "AttachStdout": False,
        "AttachStderr": False,
        "Tty": True,
    }

    port = None
    if cmd:
        s, m, r = container_processes(username, cid, cmd)
        if s == 0:
            return (s, "", r)
        else:
            port = r
            params["Cmd"] = ["/bin/sh", "-c", base_cmd % (r, "False", cmd)]
    else:
        params["Cmd"] = [
            "/bin/sh",
            "-c",
            base_cmd % (DEFAULT_CONSOLE_PORT_START, "True", "bash")
        ]
    # 创建一个 Exec 实例
    req = requests.post(
        url=url + "/containers/%s/exec" % cid,
        headers=headers,
        data=json.dumps(params)
    )
    status = req.status_code
    if status != 201:
        return (status, req.text, "")

    # 启动 Exec 实例
    r = requests.post(
        url=url + "/exec/%s/start" % req.json()["Id"],
        headers=headers,
        data=json.dumps({"Tty": True, "Detach": True})
    )
    s = r.status_code
    if s != 200:
        return (s, r.text, "")
    s1, m1, r1 = container_console_save(username, cid, cmd, port)
    if s1 != 0:
        return (s1, m1, "")
    return (s1, "", r1)


def container_console_md5(username, cid, cmd):
    """ 根据用户名、容器ID、命令生成唯一的 md5 url 地址 """
    random_str = username + cid + cmd
    hash_str = cid[0:12] + hashlib.md5(random_str).hexdigest()[0:12]
    return "http://%s.%s.%s" % (
        hash_str,
        username,
        DEFAULT_CONSOLE_DOMAIN
    )


def container_console_save(username, cid, cmd=None, port=None):
    """ 保存用户的 Console 地址到 Redis 中。"""

    # 获取容器所在 nginx 网络的 IP 地址
    s, m, r = container_inspect(cid)
    if s != 200:
        return (s, m, "")
    cip = r["NetworkSettings"]["Networks"]["fuvism-nginx"]["IPAddress"]
    rconn = redis.Redis(host="127.0.0.1", port=6379, db=0)

    if cmd and port:
        console_url = container_console_md5(username, cid, cmd)
        console_addr = "http://%s:%d" % (cip, port)
        rconn.set(console_url, console_addr)
        return (0, "", console_url)
    else:
        # 第一次创建容器后，默认在 redis 中保存 ssh、8000 地址
        r = []
        for c in ["ssh", "8000"]:
            console_url = "http://%s.%s.%s" % (
                c,
                username,
                DEFAULT_CONSOLE_DOMAIN,
            )
            r.append(console_url)
            console_addr = "http://%s:%d" % (cip, DEFAULT_CONSOLE_PORT_START)
            if c == "8000":
                console_addr = "http://%s:%d" % (cip, 8000)
            rconn.set(console_url, console_addr)
        return (0, "", r)


def container_delete(username, cid):
    """ 删除容器，同时删除 Redis 中的 URL 地址 """

    r = requests.delete(url=url + "/containers/%s?force=true" % cid)
    s = r.status_code
    if s != 204:
        return (s, r.text, "")

    # 删除该用户相关的所有域名解析
    rconn = redis.Redis(host="127.0.0.1", port=6379, db=0)
    urls = rconn.keys("*.%s.%s" % (username, DEFAULT_CONSOLE_DOMAIN))
    rconn.delete(*urls)
    return (s, "", "")


def host_read_files(files):
    """ 读取共享存储中文件的内容 """

    content = {}
    for f in files:
        # 文件在共享存储上所在的路径
        fp = os.path.dirname(f)
        if not os.path.exists(fp):
            os.makedirs(fp)

        # 如果文件不存在, 写入默认内容
        if not os.path.exists(f):
            fo = open(f, "w")
            if not (files[f]):
                fo.write("")
            else:
                fo.writelines(files[f].encode("utf-8"))
            fo.close()
            content[f] = files[f]
        else:
            # 获取文件的类型
            p = subprocess.Popen(["file %s" % f],
                                 stdout=subprocess.PIPE,
                                 shell=True)
            data = p.stdout.read()
            p.stdout.close()

            # 判断文件是否为普通文本类型，并读取文件内容
            if "text" in data or "empty" in data:
                fo = open(f)
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


def host_write_files(files):
    """ 写入文件内容到共享存储中 """

    for f in files:
        # 文件在共享存储上所在的路径
        fp = os.path.dirname(f)
        if not os.path.exists(fp):
            os.makedirs(fp)
        # 写入数据到文件中
        fo = open(f, "w")
        if not files[f]:
            fo.write("")
        else:
            fo.writelines(files[f].encode("utf-8"))

        fo.close()

    return (0, "", "")


def host_exec(cmds):
    """在 Docker 主机上执行命令"""

    has_error = {}
    for cmd in cmds:
        p = subprocess.Popen([cmd],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             shell=True)
        out, err = p.communicate()
        if err:
            has_error = {"error": err}
            break
    if not has_error:
        return (0, "", "")

    return (1, has_error, "")


if __name__ == "__main__":
    # print container_delete("longgeek", "f3ea0d01f44faa2f3b98bcf57431d34")
    # print container_create(
    #     "longgeek",
    #     "192.168.80.117:5000/longgeek/ubuntu-14.04.1:base"
    # )

    # import time
    # import threading
    # for i in range(1):
    #     p = threading.Thread(
    #         target=create,
    #         args=("longgeek",
    #               "192.168.80.117:5000/longgeek/ubuntu-14.04.1:base")
    #     )
    #     p.start()
    # print container_console("longgeek",
    #                         "246a8b27405b540bdee57c5b865baf4",
    #                         base_cmd)
    # print container_console("longgeek",
    #                         "f3ea0d01f44faa2f3b98bcf57431d34",
    #                         "ipython")
    # print container_exec("0f645a0f80489f16fd1991949601186",
    #                      ["cat /etc/hosts", "sleep 2", "touch /bbb"])
    # print host_read_files(
    #     {
    #         "/storage/user_data/longgeek/learn/online_course/ \
    #         course_c9/part_cb/stage_cb/task_bb/simple.py": "print bbb",
    #         "/storage/user_data/longgeek/learn/online_course/ \
    #         course_c9/part_cb/stage_cb/task_bb/simple1.py": "print ccc"
    #     }
    # )
    # print host_write_files(
    #     {
    #         "/storage/user_data/longgeek/learn/online_course/ \
    #         course_c9/part_cb/stage_cb/task_bb/simple.py": "print 111",
    #         "/storage/user_data/longgeek/learn/online_course/ \
    #         course_c9/part_cb/stage_cb/task_bb/simple2.py": "print 222"
    #     }
    # )
    print host_exec(["mkdir /tmp/a", "mkdir /tmp/b"])
