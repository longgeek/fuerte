#!/bin/bash

IP=$(ifconfig eth0 | grep 'inet addr:' | awk '{print $2}' | awk -F: '{print $2}')

# consul 没有使用 TLS 证书的情况下
# docker run -itd \
# -p 4000:4000 \
# --name fuvism-swarm-manage \
# --restart always \
# -v /storage/services/ca:/certs.d/ca:ro \
# -v /storage/services/swarm:/certs.d/swarm:ro \
# swarm manage \
# -H :4000 \
# --replication \
# --advertise 192.168.0.1:4000 \
# --strategy binpack \
# --tlsverify \
# --tlscacert=/certs.d/ca/ca.pem \
# --tlscert=/certs.d/swarm/swarm.pem \
# --tlskey=/certs.d/swarm/swarm-key.pem \
# consul://192.168.0.1:8500


# consul 使用了 TLS 证书
# --strategy binpack \
docker run -itd \
-p 4000:4000 \
--name fuvism-swarm-manage \
--restart always \
-v /storage/services/ca:/certs.d/ca:ro \
-v /storage/services/swarm:/certs.d/swarm:ro \
-v /storage/services/client:/certs.d/client:ro \
swarm manage \
-H :4000 \
--replication \
--advertise $IP:4000 \
--tlsverify \
--tlscacert=/certs.d/ca/ca.pem \
--tlscert=/certs.d/swarm/swarm.pem \
--tlskey=/certs.d/swarm/swarm-key.pem \
--discovery-opt kv.cacertfile=/certs.d/ca/ca.pem \
--discovery-opt kv.certfile=/certs.d/client/client.pem \
--discovery-opt kv.keyfile=/certs.d/client/client-key.pem \
consul://192.168.0.1:8501
