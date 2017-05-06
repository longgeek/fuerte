#!/bin/bash


# 检查是否有 consul 的 ceph rbd 存储
/bin/echo -e "\n1. 检测 rbd 存储..."
POINT="/storage/services/consul/data"
M_OPTS="-t xfs -o rw,noexec,nodev,noatime,nodiratime,nobarrier,discard"

rbd info FUVISM_CONSUL > /dev/null
if [ $? = 0 ]; then
    /bin/echo "    rbd 存储已存在"
    MAP_NUM=$(rbd showmapped | grep FUVISM_CONSUL | wc -l)
    if [ $MAP_NUM = 0 ]; then
        MAPD=$(rbd map FUVISM_CONSUL)
        [ -e $POINT ] || mkdir $POINT
        mount $M_OPTS $MAPD $POINT
    else
        MOUNT_NUM=$(mount -l | grep $POINT | wc -l)
        [ $MOUNT_NUM = 0 ] && \
        MAPD=$(rbd showmapped | grep FUVISM_CONSUL | awk '{print $5}') && \
        mount $M_OPTS $MAPD $POINT
    fi
    /bin/echo "    rbd 存储已挂载"
else
    /bin/echo "    rbd 存储不存在, 开始自动创建..."
    rbd create rbd/FUVISM_CONSUL -s 5G --image-feature layering &> /dev/null
    MAPD=$(rbd map FUVISM_CONSUL)
    mkfs -t xfs $MAPD &> /dev/null
    [ -e $POINT ] || mkdir $POINT
    mount $M_OPTS $MAPD $POINT
    /bin/echo -e "    存储已创建，并挂载.\n"
fi

/bin/echo -e "\n2. 创建 Consul 容器"

CONTAINER_NUM=$(docker ps -a | grep fuvism-consul | wc -l)
if [ $CONTAINER_NUM = 0 ]; then
    CID=$(
        docker run -itd --restart always --name fuvism-consul \
            -v /storage/services/consul:/consul/config \
            -v /storage/services/ca/ca.pem:/consul/config/ca.pem \
            -p 8501:8501 \
            consul:latest \
            agent \
            -advertise=192.168.0.1 \
            -data-dir=/consul/config/data \
            -config-dir=/consul/config \
            -config-file=/consul/config/server.json
    )
    /bin/echo "    容器 ID: $CID"
else
    /bin/echo "    容器已存在."
fi
