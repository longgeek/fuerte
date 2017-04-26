#!/bin/bash

# 检查是否有 mysql 的 ceph rbd 存储
/bin/echo -e "\n1. 检测 rbd 存储..."
POINT="/storage/services/mysql"
M_OPTS="-t xfs -o rw,noexec,nodev,noatime,nodiratime,nobarrier,discard"

rbd info FUVISM_MYSQL > /dev/null
if [ $? = 0 ]; then
    /bin/echo "    rbd 存储已存在"
    MAP_NUM=$(rbd showmapped | grep FUVISM_MYSQL | wc -l)
    if [ $MAP_NUM = 0 ]; then
        MAPD=$(rbd map FUVISM_MYSQL)
        [ -e $POINT ] || mkdir $POINT
        mount $M_OPTS $MAPD $POINT
    else
        MOUNT_NUM=$(mount -l | grep $POINT | wc -l)
        [ $MOUNT_NUM = 0 ] && \
        MAPD=$(rbd showmapped | grep FUVISM_MYSQL | awk '{print $5}') && \
        mount $M_OPTS $MAPD $POINT
    fi
    /bin/echo "    rbd 存储已挂载"
else
    /bin/echo "    rbd 存储不存在, 开始自动创建..."
    rbd create rbd/FUVISM_MYSQL -s 5G --image-feature layering &> /dev/null
    MAPD=$(rbd map FUVISM_MYSQL)
    mkfs -t xfs $MAPD &> /dev/null
    [ -e $POINT ] || mkdir $POINT
    mount $M_OPTS $MAPD $POINT
    /bin/echo -e "    存储已创建，并挂载.\n"
fi

/bin/echo -e "\n2. 创建 Mysql 容器"

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
            --collation-server=utf8mb4_unicode_ci \
            --wait_timeout=604800
    )
    /bin/echo "    容器 ID: $CID"
else
    /bin/echo "    容器已存在."
fi
