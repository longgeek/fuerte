#!/bin/bash

[ -e ~/.docker ] || mkdir ~/.docker
cp /storage/services/ca/ca.pem ~/.docker/
cp /storage/services/client/client.pem ~/.docker/cert.pem
cp /storage/services/client/client-key.pem ~/.docker/key.pem

docker --tlsverify -H:4000 ps
