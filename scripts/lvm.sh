#!/bin/bash

apt-get install -y lvm2
pvcreate /dev/vdd1
vgcreate vg-ceph-storage /dev/vdd1
lvcreate -L SIZEG -n lv-ceph-storage vg-ceph-storage
mkfs -t xfs -m crc=0 -n ftype=1 -f /dev/vg-ceph-storage/lv-ceph-storage
mkdir -p /ceph/osd
vim /etc/fstab
# /dev/vg-ceph-storage/lv-ceph-storage  /ceph/osd xfs  rw,relatime,attr2,inode64,prjquota  0  0

#
# 在线扩容
#
pvcreate /dev/vdd1
vgextend vg-ceph-storage /dev/vdd1
lvextend -L +SIZEG /dev/vg-ceph-storage/lv-ceph-storage
xfs_growfs /dev/vg-ceph-storage/lv-ceph-storage
