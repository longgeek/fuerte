#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Longgeek <longgeek@fuvism.com>

import inspect


def is_start(username, cid):
    """检测容器是否启动

    :param str cid: The container uuid
    """

    # 获取容器的详细信息
    s_inspect, m_inspect, r_inspect = inspect.inspect(cid)
    if s_inspect != 200:
        return (s_inspect, m_inspect, r_inspect)
    if r_inspect["State"]["Running"]:
        return (0, "", "")
    else:
        return (404, "", "")
