#!/bin/bash
#http://www.aboutyun.com/thread-10662-1-1.html

echo "deb http://mirrors.aliyun.com/ceph/debian-jewel/ trusty main" > /etc/apt/sources.list.d/ceph.list
apt-get update
apt-get install -y --force-yes ceph ceph-deploy ceph-fs-common ceph-fuse ceph-mds
cd /etc/ceph
ceph-deploy new dc-manager01 dc-manager02 dc-manager03
ceph-deploy install dc-manager01 dc-manager02 dc-manager03
ceph-deploy mon create dc-manager01 dc-manager02 dc-manager03
ceph-deploy gatherkeys dc-manager01 dc-manager02 dc-manager03
ceph-deploy mds create dc-manager01 dc-manager02 dc-manager03
mkdir -p /ceph/osd
chown ceph:ceph /ceph/osd
echo "/dev/vg-ceph-storage/lv-ceph-storage  /ceph/osd xfs  rw,relatime,attr2,inode64,prjquota  0  0" >> /etc/fstab
ceph-deploy osd prepare dc-manager01:/ceph/osd dc-manager02:/ceph/osd dc-manager03:/ceph/osd
ceph-deploy osd activate dc-manager01:/ceph/osd dc-manager02:/ceph/osd dc-manager03:/ceph/osd
ceph-deploy admin dc-manager01

###############################################
# 版本大于 0.8 需要手工创建 metadata
ceph osd pool create cephfs_data 0
ceph osd pool create cephfs_metadata 0
ceph fs new cephfs cephfs_metadata cephfs_data
###############################################

echo "mon clock drift allowed = 1" >> ceph.conf
ceph-deploy --overwrite-conf config push dc-manager01 dc-manager02 dc-manager03

ceph -s
ceph osd tree
restart ceph-all
#mount.ceph dc-manager01,dc-manager02,dc-manager03:/ /storage -o name=admin,secret=AQC50tNYCCWlBRAAdy1epXR6OX3vzkIf4uVxPg==
#echo "dc-manager01,dc-manager02,dc-manager03:/        /storage ceph name=admin,secret=AQCxodRYAKBDIRAAv+QTchsG1jM1I0EzP4r2yA== 0      0" >> /etc/fstab
