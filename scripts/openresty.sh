#!/bin/bash

docker run \
    -itd \
    -p 80:80 \
    --net fuvism-nginx \
    --name c.fuvism.com \
    -v /opt/git/fuerte/install/openresty/nginx.conf:/usr/local/openresty/nginx/conf/nginx.conf \
    -v /opt/git/fuerte/install/openresty/nginx-bp:/usr/local/openresty/nginx/conf/nginx-bp \
    -v /opt/git/fuerte/install/openresty/sites-enabled:/usr/local/openresty/nginx/conf/sites-enabled \
    -v /opt/git/fuerte/install/openresty/assets:/usr/local/openresty/nginx/html/assets \
    openresty/openresty:trusty
