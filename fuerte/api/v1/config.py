#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Longgeek <longgeek@fuvism.com>

from fuerte import app


CONSOLE_DOMAIN = app.config["CONSOLE_DOMAIN"]
CONSOLE_PORT_BEG = app.config["CONSOLE_PORT_BEG"]
CONSOLE_PORT_END = app.config["CONSOLE_PORT_END"]
NETWORK_BASES_NAME = app.config["NETWORK_BASES_NAME"]
NETWORK_NGINX_NAME = app.config["NETWORK_NGINX_NAME"]

URL = app.config["URL"]
HEADERS = {"content-type": "application/json"}
BASE_CMD = "/storage/.system/.console/bin/butterfly.server.py \
     --unsecure \
     --host=0.0.0.0 \
     --port=%d \
     --login=%s \
     --cmd=%s"

# API Actions
API_ACTIONS = {
    "Container": {
        "Create": {     # 查看学习环境的状态，包括了启动状态和结束状态
            "action": ("container", "create", "create"),
        },
    }
}


def load_workflow(api_key, api_action):
    """ 加载 API 的 Wrokflow """

    package, moduler, func = API_ACTIONS[api_key][api_action]["action"]
    workflow = getattr(
        __import__(
            "fuerte.api.v1.actions.%s.%s" % (package, moduler),
            fromlist=[func]
        ),
        func
    )

    return (0, "Success!", workflow)
