#!/bin/bash

curl -v -s -k \
    --key /etc/docker/certs.d/client/client-key.pem \
    --cert /etc/docker/certs.d/client/client.pem \
    https://192.168.80.117:2375/images/json
