#!/bin/bash

[ -e /sbin/mkfs.xfs ] || echo "mkfs.xfs not install"
[ -e /sbin/mkfs.xfs ] || exit

apt-get install -y lvm2
pvcreate /dev/vdc1
vgcreate vg-docker-storage /dev/vdc1
lvcreate -L 9.9G -n lv-docker-storage vg-docker-storage
service docker stop
rm -fr /var/lib/docker/*
mkfs -t xfs -m crc=0 -n ftype=1 -f /dev/vg-docker-storage/lv-docker-storage
echo "/dev/vg-docker-storage/lv-docker-storage  /var/lib/docker xfs  rw,relatime,attr2,inode64,prjquota  0  0" >> /etc/fstab
mount -a
#
# 在线扩容
#
# pvcreate /dev/vdc1
# vgextend vg-docker-storage /dev/vdc1
# lvextend -L +SIZEG /dev/vg-docker-storage/lv-docker-storage
# xfs_growfs /dev/vg-docker-storage/lv-docker-storage
