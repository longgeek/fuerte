#!/bin/bash

docker run \
    -itd \
    --name fuvism-boss \
    --net fuvism-manager \
    --restart always \
    --link fuvism-mysql \
    --link fuvism-memcached \
    fuvism/boss:latest
