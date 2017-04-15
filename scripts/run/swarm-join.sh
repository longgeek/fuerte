#!/bin/bash

IP=$(ifconfig eth0 | grep 'inet addr:' | awk '{print $2}' | awk -F: '{print $2}')
# consul 没有使用 TLS 证书的情况下
# docker run -itd \
# --name fuvism-swarm-node \
# --restart always \
# swarm join \
# --advertise 192.168.0.2:2375 \
# consul://192.168.0.2:8500


# consul 使用了 TLS 证书
docker run -itd \
--name fuvism-swarm-node \
--restart always \
-v /storage/services/ca:/certs.d/ca:ro \
-v /storage/services/client:/certs.d/client:ro \
swarm join \
--advertise $IP:2375 \
--discovery-opt kv.cacertfile=/certs.d/ca/ca.pem \
--discovery-opt kv.certfile=/certs.d/client/client.pem \
--discovery-opt kv.keyfile=/certs.d/client/client-key.pem \
consul://192.168.0.2:8501
