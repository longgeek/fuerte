#!/bin/bash

curl -v -s -k \
    --key /storage/services/client/client-key.pem \
    --cert /storage/services/client/client.pem \
    https://192.168.0.2:2375/images/json
