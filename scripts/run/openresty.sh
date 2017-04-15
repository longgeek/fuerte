#!/bin/bash

docker run \
    -itd \
    -p 80:80 \
    --net fuvism-nginx \
    --name fuvism-nginx \
    --link fuvism-looker \
    --link fuvism-boss \
    --link fuvism-zion \
    --link fuvism-op \
    --link fuvism-prerender \
    --restart always \
    -v /opt/git:/opt/git \
    -v /opt/git/fuerte/install/openresty/nginx.conf:/usr/local/openresty/nginx/conf/nginx.conf \
    -v /opt/git/fuerte/install/openresty/nginx-bp:/usr/local/openresty/nginx/conf/nginx-bp \
    -v /opt/git/fuerte/install/openresty/sites-enabled:/usr/local/openresty/nginx/conf/sites-enabled \
    -v /opt/git/fuerte/install/openresty/assets:/usr/local/openresty/nginx/html/assets \
    fuvism/openresty:latest

docker network connect fuvism-manager fuvism-nginx
