#!/bin/bash

# 检查是否有 registry 的 ceph rbd 存储
/bin/echo -e "\n1. 检测 rbd 存储..."
POINT="/storage/services/registry/data"
M_OPTS="-t xfs -o rw,noexec,nodev,noatime,nodiratime,nobarrier,discard"

rbd info FUVISM_REGISTRY > /dev/null
if [ $? = 0 ]; then
    /bin/echo "    rbd 存储已存在"
    MAP_NUM=$(rbd showmapped | grep FUVISM_REGISTRY | wc -l)
    if [ $MAP_NUM = 0 ]; then
        MAPD=$(rbd map FUVISM_REGISTRY)
        [ -e $POINT ] || mkdir $POINT
        mount $M_OPTS $MAPD $POINT
    else
        MOUNT_NUM=$(mount -l | grep $POINT | wc -l)
        [ $MOUNT_NUM = 0 ] && \
        MAPD=$(rbd showmapped | grep FUVISM_REGISTRY | awk '{print $5}') && \
        mount $M_OPTS $MAPD $POINT
    fi
    /bin/echo "    rbd 存储已挂载"
else
    /bin/echo "    rbd 存储不存在, 开始自动创建..."
    rbd create rbd/FUVISM_REGISTRY -s 10G --image-feature layering &> /dev/null
    MAPD=$(rbd map FUVISM_REGISTRY)
    mkfs -t xfs $MAPD &> /dev/null
    [ -e $POINT ] || mkdir $POINT
    mount $M_OPTS $MAPD $POINT
    /bin/echo -e "    存储已创建，并挂载.\n"
fi

/bin/echo -e "\n2. 创建 Registry 容器"

CONTAINER_NUM=$(docker ps -a | grep fuvism-registry | wc -l)
if [ $CONTAINER_NUM = 0 ]; then
    CID=$(
        docker run -itd \
            -p 5000:5000 \
            --restart=always \
            --name fuvism-registry \
            -v /storage/services/registry/:/etc/registry \
            -v /storage/services/registry/data:/var/lib/registry \
            -e REGISTRY_HTTP_TLS_CERTIFICATE=/etc/registry/registry.pem \
            -e REGISTRY_HTTP_TLS_KEY=/etc/registry/registry-key.pem \
            -e REGISTRY_HTTP_HOST=https://192.168.0.1:5000 \
            -e REGISTRY_AUTH=htpasswd \
            -e REGISTRY_AUTH_HTPASSWD_REALM=Registry-Realm \
            -e REGISTRY_AUTH_HTPASSWD_PATH=/etc/registry/registry.htpasswd \
            -e REGISTRY_STORAGE_DELETE_ENABLED=true \
            registry:2
    )
    /bin/echo "    容器 ID: $CID"
else
    /bin/echo "    容器已存在."
fi

