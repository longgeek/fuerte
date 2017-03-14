#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Longgeek <longgeek@fuvism.com>

import os
import subprocess
import simplejson as json


def read_files(files):
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


def write_files(files):
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
