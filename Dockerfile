FROM ubuntu:14.04.5
MAINTAINER longgeek@fuvism.com


#
# 时区和中文环境设置
#
RUN echo "Asia/Shanghai" > /etc/timezone && \
    dpkg-reconfigure -f noninteractive tzdata && \
    locale-gen en_US.UTF-8 && \
    DEBIAN_FRONTEND=noninteractive dpkg-reconfigure locales && \
    locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:us
ENV LC_ALL en_US.UTF-8


#
# 基本 Bash 设置
#
RUN echo "\n\
alias ls='ls -G --color=auto'\n\
alias ll='ls -la'\n\
alias l='ls -l'\n\
alias grep='grep --color'\n\
export CLICOLOR=1\n\
export LS_COLORS='ex=35:ln=36:mi=31:or=31'\n\
" >> /root/.bashrc


#
# 设置阿里云源
# 安装基本软件包
#
RUN echo "\n\
deb http://mirrors.aliyun.com/ubuntu/ trusty main restricted universe multiverse\n\
deb http://mirrors.aliyun.com/ubuntu/ trusty-security main restricted universe multiverse\n\
deb http://mirrors.aliyun.com/ubuntu/ trusty-updates main restricted universe multiverse\n\
deb http://mirrors.aliyun.com/ubuntu/ trusty-proposed main restricted universe multiverse\n\
deb http://mirrors.aliyun.com/ubuntu/ trusty-backports main restricted universe multiverse\n\
deb-src http://mirrors.aliyun.com/ubuntu/ trusty main restricted universe multiverse\n\
deb-src http://mirrors.aliyun.com/ubuntu/ trusty-security main restricted universe multiverse\n\
deb-src http://mirrors.aliyun.com/ubuntu/ trusty-updates main restricted universe multiverse\n\
deb-src http://mirrors.aliyun.com/ubuntu/ trusty-proposed main restricted universe multiverse\n\
deb-src http://mirrors.aliyun.com/ubuntu/ trusty-backports main restricted universe multiverse\n\
" > /etc/apt/sources.list && \
    apt-get update && \
    apt-get -y install vim ipython openssh-server python-pip python-dev libffi-dev python-openssl \
                       python-crypto libssl-dev dstat htop tmux git man-db telnet


#
# 设置 Vim
#
RUN echo "\n\
set nu\n\
set noswapfile\n\
set smartindent\n\
set autoindent\n\
set tabstop=4\n\
set shiftwidth=4\n\
set softtabstop=4\n\
set smarttab\n\
set expandtab\n\
set shiftround\n\
set autoread\n\
set fileencodings=utf-8,ucs-bom,gb18030,gbk,gb2312,cp936\n\
set termencoding=utf-8\n\
set encoding=utf-8\n\
colorscheme Tomorrow-Night\n\
" >> /etc/vim/vimrc && \
    mkdir /etc/vim/colors && \
    wget https://raw.githubusercontent.com/chriskempson/tomorrow-theme/master/vim/colors/Tomorrow-Night.vim -P /etc/vim/colors/


#
# 执行 Bash
#
CMD ["bash"]
