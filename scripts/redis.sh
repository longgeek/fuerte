#!/bin/bash

# 检查是否有 redis 的 ceph rbd 存储
echo -e "\n1. 检测 rbd 存储..."
rbd info FUVISM_REDIS &> /dev/null

if [ $? = 0 ]; then
    echo "    rbd 存储已存在"
    MAP_NUM=$(rbd showmapped | grep FUVISM_REDIS | wc -l)
    if [ $MAP_NUM = 0 ]; then
        MAPD=$(rbd map FUVISM_REDIS)
        [ -e /storage/services/redis ] || mkdir /storage/services/redis
        mount -t ext4 $MAPD /storage/services/redis
    else
        MOUNT_NUM=$(mount -l | grep "/storage/services/redis" | wc -l)
        [ $MOUNT_NUM = 0 ] && \
        MAPD=$(rbd showmapped | grep FUVISM_REDIS | awk '{print $5}') && \
        mount -t ext4 $MAPD /storage/services/redis
    fi
    echo "    rbd 存储已挂载"
else
    echo "    rbd 存储不存在, 开始自动创建..."
    rbd create rbd/FUVISM_REDIS -s 5G --image-feature layering &> /dev/null
    MAPD=$(rbd map FUVISM_REDIS)
    mkfs -t ext4 $MAPD &> /dev/null
    [ -e /storage/services/redis ] || mkdir /storage/services/redis
    mount -t ext4 $MAPD /storage/services/redis
    echo -e "    存储已创建，并挂载.\n"
fi

echo -e "\n2. 创建 Redis 容器"

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
    echo "    容器 ID: $CID"
else
    echo "    容器已存在."
fi
