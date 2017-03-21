#!/bin/bash

CONTAINER_ID="fb"
#首先得到容器进程的pid
CON_PID=$(docker inspect '--format={{ .State.Pid }}' $CONTAINER_ID)
#首先得到容器的命名空间目录
CON_NET_SANDBOX=$(docker inspect '--format={{ .NetworkSettings.SandboxKey }}' $CONTAINER_ID)
echo $CON_NET_SANDBOX
#在netns目录下创建至容器网络名字空间的链接，方便下面在docker主机上执行ip netns命令对容器的网络名字空间进行操作
mkdir -p /var/run/netns
ln -s $CON_NET_SANDBOX /var/run/netns/$CON_PID
#获取主机虚拟网卡ID
VETH_ID=$(ip netns exec $CON_PID ip link show eth1|head -n 1|awk -F: '{print $1}')
#获取主机虚拟网卡名称
VETH_NAME=$(ip link|grep -e "${VETH_ID}:"|awk '{print $2}'|awk -F@ '{print $1}')
echo $VETH_NAME
#最后删除在netns目录下创建的链接
rm -f /var/run/netns/$CON_PID
