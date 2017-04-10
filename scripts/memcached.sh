#!/bin/bash

docker run \
    -itd \
    --name fuvism-memcached \
    --net fuvism-manager \
    --restart always \
    memcached:1.4.36 -m 64
