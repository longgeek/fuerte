#!/bin/bash

# consul 没有使用 TLS 证书的情况下
# docker run --rm \
# swarm list \
# consul://192.168.0.1:8500


# consul 使用了 TLS 证书
docker run --rm \
-v /storage/services/ca:/certs.d/ca:ro \
-v /storage/services/swarm:/certs.d/swarm:ro \
-v /storage/services/client:/certs.d/client:ro \
swarm list \
--discovery-opt kv.cacertfile=/certs.d/ca/ca.pem \
--discovery-opt kv.certfile=/certs.d/client/client.pem \
--discovery-opt kv.keyfile=/certs.d/client/client-key.pem \
consul://192.168.0.1:8501
