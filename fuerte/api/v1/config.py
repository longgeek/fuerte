#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Longgeek <longgeek@fuvism.com>

from fuerte import app


NODE_IP = app.config["NODE_IP"]
CONSOLE_DOMAIN = app.config["CONSOLE_DOMAIN"]
CONSOLE_PORT_BEG = app.config["CONSOLE_PORT_BEG"]
CONSOLE_PORT_END = app.config["CONSOLE_PORT_END"]
NETWORK_BASES_NAME = app.config["NETWORK_BASES_NAME"]
NETWORK_NGINX_NAME = app.config["NETWORK_NGINX_NAME"]

TLS = app.config["TLS"]
TLS_CERTS = app.config["TLS_CERTS"]

CEPH_CONF = "/etc/ceph/ceph.conf"

URL = app.config["URL"]
HEADERS = {"content-type": "application/json"}
BASE_CMD = "/storage/.system/.console/bin/butterfly.server.py \
     --unsecure \
     --host=0.0.0.0 \
     --port=%s \
     --login=%s \
     --cmd=%s"

# API Actions
API_ACTIONS = {
    "Container": {
        "Create": {
            "action": ("container", "create", "create"),
        },
        "Delete": {
            "action": ("container", "delete", "delete"),
        },
        "Console": {
            "action": ("container", "console", "console"),
        },
        "Exec": {
            "action": ("container", "exec", "execute"),
        },
    },
    "Host": {
        "Exec": {
            "action": ("host", "exec", "execute"),
        },
        "ReadFiles": {
            "action": ("host", "host", "read_files"),
        },
        "WriteFiles": {
            "action": ("host", "host", "write_files"),
        },
        "CreateContainerExtendNet": {
            "action": ("host", "container", "create_container_extend_net"),
        },
        "CreateContainerExtendDisk": {
            "action": ("host", "container", "create_container_extend_disk"),
        },
    }

}


def load_api(api_key, api_action):
    """ 加载 API 的 Action """

    package, moduler, func = API_ACTIONS[api_key][api_action]["action"]
    load_action = getattr(
        __import__(
            "fuerte.api.v1.actions.%s.%s" % (package, moduler),
            fromlist=[func]
        ),
        func
    )

    return (0, "Success!", load_action)
