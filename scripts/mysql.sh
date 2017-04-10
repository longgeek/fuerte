#!/bin/bash

# 检查是否有 mysql 的 ceph rbd 存储
echo -e "\n1. 检测 rbd 存储..."
rbd info FUVISM_MYSQL &> /dev/null

if [ $? = 0 ]; then
    echo "    rbd 存储已存在"
    MAP_NUM=$(rbd showmapped | grep FUVISM_MYSQL | wc -l)
    if [ $MAP_NUM = 0 ]; then
        MAPD=$(rbd map FUVISM_MYSQL)
        [ -e /storage/services/mysql ] || mkdir /storage/services/mysql
        mount -t ext4 $MAPD /storage/services/mysql
    else
        MOUNT_NUM=$(mount -l | grep "/storage/services/mysql" | wc -l)
        [ $MOUNT_NUM = 0 ] && \
        MAPD=$(rbd showmapped | grep FUVISM_MYSQL | awk '{print $5}') && \
        mount -t ext4 $MAPD /storage/services/mysql
    fi
    echo "    rbd 存储已挂载"
else
    echo "    rbd 存储不存在, 开始自动创建..."
    rbd create rbd/FUVISM_MYSQL -s 5G --image-feature layering &> /dev/null
    MAPD=$(rbd map FUVISM_MYSQL)
    mkfs -t ext4 $MAPD &> /dev/null
    [ -e /storage/services/mysql ] || mkdir /storage/services/mysql
    mount -t ext4 $MAPD /storage/services/mysql
    echo -e "    存储已创建，并挂载.\n"
fi

echo -e "\n2. 创建 Mysql 容器"

CONTAINER_NUM=$(docker ps -a | grep fuvism-mysql | wc -l)
if [ $CONTAINER_NUM = 0 ]; then
    CID=$(
        docker run \
            -itd \
            --restart always \
            --name fuvism-mysql \
            --net fuvism-manager \
            -v /storage/services/mysql:/var/lib/mysql \
            -e MYSQL_ROOT_PASSWORD=4jT3R4fEjQRz8n8s \
            mysql:5.6 \
            --character-set-server=utf8mb4 \
            --collation-server=utf8mb4_unicode_ci
    )
    echo "    容器 ID: $CID"
else
    echo "    容器已存在."
fi
