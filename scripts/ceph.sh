#!/bin/bash
#http://www.aboutyun.com/thread-10662-1-1.html

apt-get install -y ceph ceph-deploy ceph-fs-common ceph-fuse
ceph-deploy new node01
ceph-deploy install node01
ceph-deploy mon create node01
ceph-deploy mds create node01
ceph-deploy gatherkeys node01
ceph-deploy osd prepare node01:/srv/ceph/osd0
ceph-deploy osd prepare node01:/srv/ceph/osd1
ceph-deploy osd activate node01:/srv/ceph/osd0
ceph-deploy osd activate node01:/srv/ceph/osd1
ceph-deploy admin node01

ceph -s
ceph osd trea
restart ceph-all
#mount.ceph manage01,node01,node02:/ /mnt -o name=admin,secret=AQC50tNYCCWlBRAAdy1epXR6OX3vzkIf4uVxPg==
