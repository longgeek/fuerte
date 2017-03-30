#!/usr/bin/env python
# encoding: utf-8

import requests
import simplejson as json
from requests.packages.urllib3.exceptions import SNIMissingWarning
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.packages.urllib3.exceptions import InsecurePlatformWarning

requests.packages.urllib3.disable_warnings(SNIMissingWarning)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)

params = {
    "action": "Container:Create",
    "params": {
        "username": "longgeek",
        "image": "192.168.0.2:5000/longgeek/ubuntu-14.04.1:base"
    }
}
r = requests.post(
    url="http://192.168.0.2:8000/api/v1",
    headers={"token": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9",
             "content-type": "application/json"},
    data=json.dumps(params),
)

print r.json()
