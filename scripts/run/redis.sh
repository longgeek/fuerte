#!/bin/bash

# 检查是否有 redis 的 ceph rbd 存储
/bin/echo -e "\n1. 检测 rbd 存储..."
POINT="/storage/services/redis"
M_OPTS="-t xfs -o rw,noexec,nodev,noatime,nodiratime,nobarrier,discard"

rbd info FUVISM_REDIS > /dev/null
if [ $? = 0 ]; then
    /bin/echo "    rbd 存储已存在"
    MAP_NUM=$(rbd showmapped | grep FUVISM_REDIS | wc -l)
    if [ $MAP_NUM = 0 ]; then
        MAPD=$(rbd map FUVISM_REDIS)
        [ -e $POINT ] || mkdir $POINT
        mount $M_OPTS $MAPD $POINT
    else
        MOUNT_NUM=$(mount -l | grep $POINT | wc -l)
        [ $MOUNT_NUM = 0 ] && \
        MAPD=$(rbd showmapped | grep FUVISM_REDIS | awk '{print $5}') && \
        mount $M_OPTS $MAPD $POINT
    fi
    /bin/echo "    rbd 存储已挂载"
else
    /bin/echo "    rbd 存储不存在, 开始自动创建..."
    rbd create rbd/FUVISM_REDIS -s 5G --image-feature layering &> /dev/null
    MAPD=$(rbd map FUVISM_REDIS)
    mkfs -t xfs $MAPD &> /dev/null
    [ -e $POINT ] || mkdir $POINT
    mount $M_OPTS $MAPD $POINT
    /bin/echo -e "    存储已创建，并挂载.\n"
fi

/bin/echo -e "\n2. 创建 Redis 容器"

CONTAINER_NUM=$(docker ps -a | grep fuvism-redis | wc -l)
if [ $CONTAINER_NUM = 0 ]; then
    CID=$(
        docker run \
            -itd \
            --restart always \
            --name fuvism-redis \
            --net fuvism-manager \
            -p 6379:6379 \
            -v /storage/services/redis:/data \
            redis:3.2.8 \
            redis-server \
            --appendonly yes \
            --requirepass YCTACMmimohBBiZRanibCnjJV8zdnwGs
    )
    /bin/echo "    容器 ID: $CID"
else
    /bin/echo "    容器已存在."
fi
