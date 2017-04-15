#!/bin/bash

clear
echo ''
echo '---------------------------------------'
echo '1. 使用阿里 apt-get 源'
echo '2. 设置 Linux 系统预留 Cache 为 10%.'
echo '3. 设置 bashrc'
echo '4. 设置 vim'
echo '5. 设置 NTP 服务器'
echo '---------------------------------------'
echo ''

set -ex
#
# 1. 使用阿里 apt-get 源
#
cp /etc/apt/sources.list /etc/apt/sources.list.bak
echo "deb http://mirrors.aliyun.com/ubuntu/ trusty main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ trusty-security main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ trusty-updates main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ trusty-proposed main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ trusty-backports main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ trusty main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ trusty-security main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ trusty-updates main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ trusty-proposed main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ trusty-backports main restricted universe multiverse" > /etc/apt/sources.list
apt-get clean all
apt-get -q update

# 
# 2. 设置 Linux 系统预留 Cache 为 10%."
# Fix: blocked for more than 120 seconds
# http://www.ttlsa.com/linux/kernel-blocked-for-more-than-120-seconds/
#
grep "vm.dirty_background_ratio = 5" /etc/sysctl.conf > /dev/null
[ $? != 0 ] && echo "vm.dirty_background_ratio = 5" >> /etc/sysctl.conf
grep "vm.dirty_ratio = 10" /etc/sysctl.conf > /dev/null
[ $? != 0 ] && echo "vm.dirty_ratio = 10" >> /etc/sysctl.conf
sysctl -p > /dev/null


#
# 3. 设置 bashrc
#
grep "ls -G --color=auto" ~/.bashrc > /dev/null
[ $? != 0 ] && echo "
alias ls='ls -G --color=auto'
alias ll='ls -la'
alias l='ls -l'
alias grep='grep --color'
export CLICOLOR=1
export LS_COLORS='ex=35:ln=36:mi=31:or=31'
" >> ~/.bashrc && source ~/.bashrc


#
# 4. 设置 vim
#
apt-get -y install vim
grep "Tomorrow-Night" /etc/vim/vimrc > /dev/null
if [ $? != 0 ]; then
    echo "
set nu
set noswapfile
set smartindent
set autoindent
set tabstop=4
set shiftwidth=4
set softtabstop=4
set smarttab
set expandtab
set shiftround
set autoread
set fileencodings=utf-8,ucs-bom,gb18030,gbk,gb2312,cp936
set termencoding=utf-8
set encoding=utf-8
colorscheme Tomorrow-Night
" >> /etc/vim/vimrc
    mkdir /etc/vim/colors && \
    wget https://raw.githubusercontent.com/chriskempson/tomorrow-theme/master/vim/colors/Tomorrow-Night.vim -P /etc/vim/colors/
fi


#
# 5. 设置 NTP 服务器
#
apt-get -y install ntp ntpdate
service ntp stop
ntpdate cn.pool.ntp.org
sed -i "s/ubuntu.pool.ntp.org/cn.pool.ntp.org/g" /etc/ntp.conf
sed -i "s/ntp.ubuntu.com/cn.pool.ntp.org/g" /etc/ntp.conf
service ntp restart
