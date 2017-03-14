#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Longgeek <longgeek@fuvism.com>

import subprocess


def h_exec(cmds):
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
