#!/bin/bash

# 测试时使用
# docker run -itd \
#     -p 192.168.8.7:8500:8500 \
#     --name=consul \
#     --restart always \
#     progrium/consul \
#     -server \
#     -bootstrap \
#     -advertise=192.168.8.7

# # 生产环境
docker run -itd --restart always --name consul \
    -v /etc/consul:/config \
    -v /storage/consul/data:/data \
    -p 8501:8501 \
    progrium/consul \
    -advertise=192.168.80.117 \
    -config-dir=/config \
    -config-file=/config/server.json
