#!/bin/bash

# # not use tls
# docker run -itd \
#     -p 127.0.0.1:5000:5000 \
#     --restart=always \
#     --name registry \
#     -v /storage/registry:/var/lib/registry \
#     registry:2

# use tls
docker run -itd \
    -p 5000:5000 \
    --restart=always \
    --name registry \
    -v /etc/registry/:/etc/registry \
    -v /storage/registry/data:/var/lib/registry \
    -e REGISTRY_HTTP_TLS_CERTIFICATE=/etc/registry/certs.d/registry.pem \
    -e REGISTRY_HTTP_TLS_KEY=/etc/registry/certs.d/registry-key.pem \
    -e REGISTRY_HTTP_HOST=https://192.168.80.117:5000 \
    -e REGISTRY_AUTH=htpasswd \
    -e REGISTRY_AUTH_HTPASSWD_REALM=Registry-Realm \
    -e REGISTRY_AUTH_HTPASSWD_PATH=/etc/registry/registry.htpasswd \
    -e REGISTRY_STORAGE_DELETE_ENABLED=true \
    registry:2
