#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Longgeek <longgeek@fuvism.com>


import ConfigParser
import simplejson as json

from redis import Redis


cfg = ConfigParser.ConfigParser()
err = "\nError: In configuration file /etc/fuerte/fuerte.conf "

if not cfg.read("/etc/fuerte/fuerte.conf"):
    exit("\nError: Can not find config file in /etc/fuerte/fuerte.conf\n")


class DefaultConfig(object):
    """Default configuration."""

    _option = "default"

    try:
        HTTP_HOST = cfg.get(_option, "http_host")
        HTTP_PORT = cfg.get(_option, "http_port")

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
    except Exception, e:
        exit(err + str(e) + "\n")
