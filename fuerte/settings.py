#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Longgeek <longgeek@fuvism.com>


import os
import fcntl
import struct
import socket
import ConfigParser


cfg = ConfigParser.ConfigParser()
err = "\nError: In configuration file /etc/fuerte/fuerte.conf "

if not cfg.read("/etc/fuerte/fuerte.conf"):
    exit("\nError: Can not find config file in \
          /etc/fuerte/fuerte.conf\n")

if not os.path.isfile("/etc/ceph/ceph.conf"):
    exit("\nError: Can not find config file in \
          /etc/ceph/ceph.conf\n")

if not os.path.isfile("/etc/ceph/ceph.client.admin.keyring"):
    exit("\nError: Can not find config file in \
          /etc/ceph/ceph.client.admin.keyring\n")


class DefaultConfig(object):
    """Default configuration."""

    _option = "default"

    try:
        URL = cfg.get(_option, "url")
        TOKEN = cfg.get(_option, "token")

        # Get current node ip address
        fuerte_interface = cfg.get(_option, "fuerte_interface")
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        NODE_IP = socket.inet_ntoa(
            fcntl.ioctl(
                s.fileno(),
                0x8915,
                struct.pack('256s', fuerte_interface[:15])
            )[20:24]
        )

        CONSOLE_DOMAIN = cfg.get(_option, "console_domain")
        CONSOLE_PORT_BEG = cfg.get(_option, "console_port_beg")
        CONSOLE_PORT_END = cfg.get(_option, "console_port_end")

        NETWORK_BASES_NAME = cfg.get(_option, "network_bases_name")
        NETWORK_NGINX_NAME = cfg.get(_option, "network_nginx_name")
    except Exception, e:
        exit(err + str(e) + "\n")


class LogConfig(object):
    """ Log configuration. """

    _option = "log"

    try:
        DEBUG = True if cfg.get(_option, "debug") == "true" else False
        VERBOSE = True if cfg.get(_option, "verbose") == "true" else False

        LOG_DIR = cfg.get(_option, "log_dir")
        LOG_FILE = cfg.get(_option, "log_file")
    except Exception, e:
        exit(err + str(e) + "\n")


class RedisConfig(object):
    """Redis Config"""

    _option = "redis"

    try:
        REDIS_HOST = cfg.get(_option, "redis_host")
        REDIS_PORT = cfg.get(_option, "redis_port")
        REDIS_DBID = cfg.get(_option, "redis_dbid")
        REDIS_PASS = cfg.get(_option, "redis_pass")
        REDIS_URL = "redis://:%s@%s:%s/%s" % (REDIS_PASS,
                                              REDIS_HOST,
                                              REDIS_PORT,
                                              REDIS_DBID)
    except Exception, e:
        exit(err + str(e) + "\n")


class SwarmConfig(object):
    """Swarm Config"""

    _option = "swarm"

    try:
        TLS = cfg.get(_option, "tls")
        TLS_CERT = cfg.get(_option, "tlscert")
        TLS_KEY = cfg.get(_option, "tlskey")
        TLS_CERTS = (TLS_CERT, TLS_KEY)
    except Exception, e:
        exit(err + str(e) + "\n")
