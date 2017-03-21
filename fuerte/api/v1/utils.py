import requests

from fuerte.api.v1.config import TLS
from fuerte.api.v1.config import TLS_CERTS
from requests.packages.urllib3.exceptions import SNIMissingWarning
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from requests.packages.urllib3.exceptions import InsecurePlatformWarning


# Disable requests the warnings
requests.packages.urllib3.disable_warnings(SNIMissingWarning)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)


def pack_requests(method, **kwargs):
    """ 为 requests 添加证书验证 """

    if TLS == "true" or TLS == "True":
        kwargs["verify"] = False
        kwargs["cert"] = TLS_CERTS

    if method == "get" or method == "GET":
        return requests.get(**kwargs)
    elif method == "post" or method == "POST":
        return requests.post(**kwargs)
    elif method == "delete" or method == "DELETE":
        return requests.delete(**kwargs)
