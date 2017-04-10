#!/bin/bash

docker run \
    -itd \
    --name fuvism-zion \
    --restart always \
    --net fuvism-manager \
    --link fuvism-redis \
    --link fuvism-looker \
    fuvism/zion:latest
