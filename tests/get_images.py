#!/usr/bin/env python
# encoding: utf-8

import requests
from requests.packages.urllib3.exceptions import SNIMissingWarning
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.packages.urllib3.exceptions import InsecurePlatformWarning

requests.packages.urllib3.disable_warnings(SNIMissingWarning)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)

r = requests.get(
    url="https://192.168.80.117:2375/images/json",
    verify=False,
    cert=("/etc/docker/certs.d/client/client.pem",
          "/etc/docker/certs.d/client/client-key.pem")
)

print r.json()
