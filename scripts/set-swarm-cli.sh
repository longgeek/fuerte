#!/bin/bash

[ -e ~/.docker ] || mkdir ~/.docker
cp /etc/docker/certs.d/ca/ca.pem ~/.docker/
cp /etc/docker/certs.d/client/client.pem ~/.docker/cert.pem
cp /etc/docker/certs.d/client/client-key.pem ~/.docker/key.pem

docker --tlsverify -H:4000 ps
