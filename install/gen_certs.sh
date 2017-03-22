#!/bin/bash -u
# https://github.com/frntn/docker-tls-helper
set -ex

SRV_SAN="DNS:node01,DNS:localhost,IP:192.168.80.117,IP:192.168.80.16,IP:192.168.80.91,IP:127.0.0.1" 
SRV_SUBJ="/CN=*"  # manage01
CLT_SUBJ="/CN=*"

CA_SUBJ="${CA_SUBJ:-"/C=${CA_C:-"FR"}/L=${CA_L:-"Paris"}/O=${CA_O:-"Ekino"}/OU=${CA_OU:-"DevOps"}/CN=${CA_CN:-"Docker TLS"}"}"
CERTS_PATH="${CERTS_PATH:-"etc/docker/certs.d"}"

#
# CA
#
create_ca() {
    [ -e ca ] || mkdir ca
    umask 177
    < /dev/urandom tr -dc "+=\-%*\!&#':;{}()[]|^~\$_2-9T-Z" | head -c65 > ca.pass
    
    # .key / .crt
    openssl req \
        -new -x509 -days ${CA_EXPIRE_DAYS:-"3650"} \
        -newkey rsa:4096 -keyout ca-key.pem -passout file:ca.pass \
        -out ca.pem -subj "${CA_SUBJ}"
}


#
# Docker Daemon
#
create_daemon() {
    [ -e daemon ] || mkdir daemon
    # .key / .csr
    openssl req -new \
        -newkey rsa:4096 -keyout daemon-key.pem -nodes \
        -out daemon.csr -subj "${SRV_SUBJ}"
    
    # .crt
    EXTFILE="extendedKeyUsage = clientAuth,serverAuth"
    [ ! -z "${SRV_SAN:-""}" ] && EXTFILE="${EXTFILE}\nsubjectAltName = ${SRV_SAN}"
    openssl x509 -req \
        -days 3650 -sha256 \
        -in daemon.csr -passin file:ca.pass \
        -CA ca.pem -CAkey ca-key.pem -CAserial ca.srl -CAcreateserial \
        -out daemon.pem \
        -extfile <(echo -e "${EXTFILE}")
}


#
# Swarm
#
create_swarm() {
    [ -e swarm ] || mkdir swarm
    # .key / .csr
    openssl req -new \
        -newkey rsa:4096 -keyout swarm-key.pem -nodes \
        -out swarm.csr -subj "${SRV_SUBJ}"
    
    # .crt
    EXTFILE="extendedKeyUsage = clientAuth,serverAuth"
    [ ! -z "${SRV_SAN:-""}" ] && EXTFILE="${EXTFILE}\nsubjectAltName = ${SRV_SAN}"
    openssl x509 -req \
        -days 3650 -sha256 \
        -in swarm.csr -passin file:ca.pass \
        -CA ca.pem -CAkey ca-key.pem -CAserial ca.srl -CAcreateserial \
        -out swarm.pem \
        -extfile <(echo -e "${EXTFILE}")
}


#
# Consul
#
create_consul() {
    [ -e consul ] || mkdir consul
    # .key / .csr
    openssl req -new \
        -newkey rsa:4096 -keyout consul-key.pem -nodes \
        -out consul.csr -subj "${SRV_SUBJ}"
    
    # .crt
    EXTFILE="extendedKeyUsage = clientAuth,serverAuth"
    [ ! -z "${SRV_SAN:-""}" ] && EXTFILE="${EXTFILE}\nsubjectAltName = ${SRV_SAN}"
    openssl x509 -req \
        -days 3650 -sha256 \
        -in consul.csr -passin file:ca.pass \
        -CA ca.pem -CAkey ca-key.pem -CAserial ca.srl -CAcreateserial \
        -out consul.pem \
        -extfile <(echo -e "${EXTFILE}")
}


#
# Registry
#
create_registry() {
    [ -e registry ] || mkdir registry
    # .key / .csr
    openssl req -new \
        -newkey rsa:4096 -keyout registry-key.pem -nodes \
        -out registry.csr -subj "${SRV_SUBJ}"
    
    # .crt
    EXTFILE="extendedKeyUsage = clientAuth,serverAuth"
    [ ! -z "${SRV_SAN:-""}" ] && EXTFILE="${EXTFILE}\nsubjectAltName = ${SRV_SAN}"
    openssl x509 -req \
        -days 3650 -sha256 \
        -in registry.csr -passin file:ca.pass \
        -CA ca.pem -CAkey ca-key.pem -CAserial ca.srl -CAcreateserial \
        -out registry.pem \
        -extfile <(echo -e "${EXTFILE}")
}


#
# Client
#
create_client() {
    [ -e client ] || mkdir client
    # .key / .csr
    openssl req -new \
        -newkey rsa:4096 -keyout client-key.pem -nodes \
        -out client.csr -subj "$CLT_SUBJ"
    
    # .crt
    EXTFILE="extendedKeyUsage = clientAuth,serverAuth"
    openssl x509 -req \
        -days 3650 -sha256 \
        -in client.csr -passin file:ca.pass \
        -CA ca.pem -CAkey ca-key.pem -CAserial ca.srl -CAcreateserial \
        -out client.pem \
        -extfile <(echo -e "${EXTFILE}")
}

#
# PERMS
#
fix_perms() {
    chmod 600 ca-key.pem swarm-key.pem client-key.pem daemon-key.pem registry-key.pem consul-key.pem
    chmod 644 ca.pem swarm.pem client.pem daemon.pem registry.pem consul.pem
    rm swarm.csr client.csr daemon.csr registry.csr consul.csr
    mv ca*.* ca/
    mv swarm*.* swarm/
    mv client*.* client/
    mv daemon*.* daemon/
    mv registry*.* registry/
    mv consul*.* consul/
}


#
# MAIN
#
main() {
    [ -e "${CERTS_PATH}" ] && rm -fr "${CERTS_PATH}"
    [ -e "${CERTS_PATH}" ] || mkdir -p "${CERTS_PATH}"
    cd "${CERTS_PATH}"
    
    create_ca
    create_daemon
    create_swarm
    create_consul
    create_registry
    create_client
    fix_perms
}

main
