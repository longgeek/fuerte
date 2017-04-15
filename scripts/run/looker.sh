#!/bin/bash

docker run \
    -itd \
    --name fuvism-looker \
    --restart always \
    --net fuvism-manager \
    --link fuvism-redis \
    --link fuvism-mysql \
    --link fuvism-memcached \
    fuvism/looker:latest
