#!/bin/bash

# consul 没有使用 TLS 证书的情况下
# docker run -itd \
# -p 4000:4000 \
# --name swarm-manage \
# --restart always \
# -v /etc/docker/certs.d/ca:/certs.d/ca:ro \
# -v /etc/docker/certs.d/swarm:/certs.d/swarm:ro \
# swarm manage \
# -H :4000 \
# --replication \
# --advertise 192.168.80.117:4000 \
# --strategy binpack \
# --tlsverify \
# --tlscacert=/certs.d/ca/ca.pem \
# --tlscert=/certs.d/swarm/swarm.pem \
# --tlskey=/certs.d/swarm/swarm-key.pem \
# consul://192.168.80.117:8500


# consul 使用了 TLS 证书
docker run -itd \
-p 4000:4000 \
--name swarm-manage \
--restart always \
-v /etc/docker/certs.d/ca:/certs.d/ca:ro \
-v /etc/docker/certs.d/swarm:/certs.d/swarm:ro \
-v /etc/docker/certs.d/client:/certs.d/client:ro \
swarm manage \
-H :4000 \
--replication \
--advertise 192.168.80.117:4000 \
--strategy binpack \
--tlsverify \
--tlscacert=/certs.d/ca/ca.pem \
--tlscert=/certs.d/swarm/swarm.pem \
--tlskey=/certs.d/swarm/swarm-key.pem \
--discovery-opt kv.cacertfile=/certs.d/ca/ca.pem \
--discovery-opt kv.certfile=/certs.d/client/client.pem \
--discovery-opt kv.keyfile=/certs.d/client/client-key.pem \
consul://192.168.80.117:8501
