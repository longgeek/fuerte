#!/bin/bash

docker run \
    -itd \
    --net fuvism-manager \
    --name fuvism-memcached \
    --restart always \
    memcached:1.4.36 -m 64
