#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Longgeek <longgeek@fuvism.com>

import requests
import simplejson as json

from fuerte.api.v1.config import URL, HEADERS


def c_exec(cid, cmds, wait=False):
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
                url=URL + "/containers/%s/exec" % cid,
                headers=HEADERS,
                data=json.dumps(params)
            )
            s = r.status_code
            if s != 201:
                return (s, r.text, "")

            r = requests.post(
                url=URL + "/exec/%s/start" % r.json()["Id"],
                headers=HEADERS,
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
                url=URL + "/containers/%s/exec" % cid,
                headers=HEADERS,
                data=json.dumps(params)
            )
            s = r.status_code
            if s != 201:
                return (s, r.text, "")

            r = requests.post(
                url=URL + "/exec/%s/start" % r.json()["Id"],
                headers=HEADERS,
                data=json.dumps({"Tty": True, "Detach": True})
            )
            s = r.status_code
            if s != 200:
                return (s, r.text, "")
        return (0, "", "")