#!/bin/bash

apt-get install -y lvm2
pvcreate /dev/vdc1
vgcreate vg-ceph-storage /dev/vdc1
lvcreate -L SIZEG -n lv-ceph-storage vg-ceph-storage
mkfs -t xfs -m crc=0 -n ftype=1 -f /dev/vg-ceph-storage/lv-ceph-storage
mount /dev/vg-ceph-storage/lv-ceph-storage /mnt


#
# 在线扩容
#
pvcreate /dev/vdd1
vgextend vg-ceph-storage /dev/vdd1
lvextend -L +SIZEG /dev/vg-ceph-storage/lv-ceph-storage
xfs_growfs /dev/vg-ceph-storage/lv-ceph-storage
