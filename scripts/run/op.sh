#!/bin/bash

docker run \
    -itd \
    --name fuvism-op \
    --restart always \
    --net fuvism-manager \
    --link fuvism-mysql \
    --link fuvism-memcached \
    fuvism/op:latest
