#!/usr/bin/env python
# encoding: utf-8

import requests
from requests.packages.urllib3.exceptions import SNIMissingWarning
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.packages.urllib3.exceptions import InsecurePlatformWarning

requests.packages.urllib3.disable_warnings(SNIMissingWarning)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)

url = "https://longgeek:123123@192.168.0.2:5000/v2/_catalog"
headers = {"cache-control": "no-cache"}

req = requests.get(
    url=url,
    headers=headers,
    verify=False,
    cert=("/storage/services/client/client.pem",
          "/storage/services/client/client-key.pem")
)

print req.json()
