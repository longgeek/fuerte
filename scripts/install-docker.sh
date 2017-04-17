#!/bin/bash

curl -sSL http://acs-public-mirror.oss-cn-hangzhou.aliyuncs.com/docker-engine/internet | sh -

apt-get upgrade
apt-get install linux-image-extra-$(uname -r) linux-image-extra-virtual

# 修改 Grub
vim /etc/default/grub
GRUB_CMDLINE_LINUX="cgroup_enable=memory swapaccount=1"

update-grub
reboot
