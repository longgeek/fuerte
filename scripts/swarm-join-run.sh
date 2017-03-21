#!/bin/bash

# consul 没有使用 TLS 证书的情况下
# docker run -itd \
# --name swarm-node \
# --restart always \
# swarm join \
# --advertise 192.168.80.117:2375 \
# consul://192.168.80.117:8500


# consul 使用了 TLS 证书
docker run -itd \
--name swarm-node \
--restart always \
-v /etc/docker/certs.d/ca:/certs.d/ca:ro \
-v /etc/docker/certs.d/client:/certs.d/client:ro \
swarm join \
--advertise 192.168.80.117:2375 \
--discovery-opt kv.cacertfile=/certs.d/ca/ca.pem \
--discovery-opt kv.certfile=/certs.d/client/client.pem \
--discovery-opt kv.keyfile=/certs.d/client/client-key.pem \
consul://192.168.80.117:8501
