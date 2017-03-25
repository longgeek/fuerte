#!/bin/bash

# 测试时使用
# docker run -itd \
#     -p 192.168.0.2:8500:8500 \
#     --name=consul \
#     --restart always \
#     progrium/consul \
#     -server \
#     -bootstrap \
#     -advertise=192.168.8.7

# # 生产环境
docker run -itd --restart always --name consul \
    -v /storage/services/consul:/config \
    -v /storage/services/ca/ca.pem:/config/ca.pem \
    -p 8501:8501 \
    progrium/consul \
    -advertise=192.168.0.2 \
    -config-dir=/config \
    -config-file=/config/server.json
