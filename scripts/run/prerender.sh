#!/bin/bash

docker run \
    -itd \
    --name fuvism-prerender \
    --restart always \
    --net fuvism-manager \
    fuvism/prerender:latest
