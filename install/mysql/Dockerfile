FROM ubuntu:16.04
MAINTAINER longgeek@fuvism.com


#
# 设置阿里云源
# 安装基本软件包
#
RUN echo "\n\
deb http://mirrors.aliyun.com/ubuntu/ xenial main restricted universe multiverse\n\
deb http://mirrors.aliyun.com/ubuntu/ xenial-security main restricted universe multiverse\n\
deb http://mirrors.aliyun.com/ubuntu/ xenial-updates main restricted universe multiverse\n\
deb http://mirrors.aliyun.com/ubuntu/ xenial-proposed main restricted universe multiverse\n\
deb http://mirrors.aliyun.com/ubuntu/ xenial-backports main restricted universe multiverse\n\
deb-src http://mirrors.aliyun.com/ubuntu/ xenial main restricted universe multiverse\n\
deb-src http://mirrors.aliyun.com/ubuntu/ xenial-security main restricted universe multiverse\n\
deb-src http://mirrors.aliyun.com/ubuntu/ xenial-updates main restricted universe multiverse\n\
deb-src http://mirrors.aliyun.com/ubuntu/ xenial-proposed main restricted universe multiverse\n\
deb-src http://mirrors.aliyun.com/ubuntu/ xenial-backports main restricted universe multiverse\n\
" > /etc/apt/sources.list && \
    apt-get update && \
    apt-get -y install vim tzdata locales apt-utils ipython openssh-server python-pip python-dev libffi-dev \
                       python-openssl python-crypto libssl-dev dstat htop tmux git man-db telnet wget


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


# add our user and group first to make sure their IDs get assigned consistently, regardless of whatever dependencies get added
RUN groupadd -r mysql && useradd -r -g mysql mysql

# add gosu for easy step-down from root
ENV GOSU_VERSION 1.7
RUN set -x \
    && apt-get update && apt-get install -y --no-install-recommends ca-certificates wget && rm -rf /var/lib/apt/lists/* \
    && wget -O /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$(dpkg --print-architecture)" \
    && wget -O /usr/local/bin/gosu.asc "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$(dpkg --print-architecture).asc" \
    && export GNUPGHOME="$(mktemp -d)" \
    && gpg --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys B42F6819007F00F88E364FD4036A9C25BF357DD4 \
    && gpg --batch --verify /usr/local/bin/gosu.asc /usr/local/bin/gosu \
    && rm -r "$GNUPGHOME" /usr/local/bin/gosu.asc \
    && chmod +x /usr/local/bin/gosu \
    && gosu nobody true \
    && apt-get purge -y --auto-remove ca-certificates wget

RUN mkdir /docker-entrypoint-initdb.d

# FATAL ERROR: please install the following Perl modules before executing /usr/local/mysql/scripts/mysql_install_db:
# File::Basename
# File::Copy
# Sys::Hostname
# Data::Dumper
RUN apt-get update && apt-get install -y perl pwgen --no-install-recommends && rm -rf /var/lib/apt/lists/*

RUN set -ex; \
# gpg: key 5072E1F5: public key "MySQL Release Engineering <mysql-build@oss.oracle.com>" imported
    key='A4A9406876FCBD3C456770C88C718D3B5072E1F5'; \
    export GNUPGHOME="$(mktemp -d)"; \
    # gpg --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys "$key"; \
    gpg --keyserver ha.pool.sks-keyservers.net --recv-keys "$key"; \
    gpg --export "$key" > /etc/apt/trusted.gpg.d/mysql.gpg; \
    rm -r "$GNUPGHOME"; \
    apt-key list > /dev/null

ENV MYSQL_MAJOR 5.7
ENV MYSQL_VERSION 5.7.18
ENV DEBIAN_FRONTEND noninteractive

# RUN echo "deb http://repo.mysql.com/apt/debian/ jessie mysql-${MYSQL_MAJOR}" > /etc/apt/sources.list.d/mysql.list

# the "/var/lib/mysql" stuff here is because the mysql-server postinst doesn't have an explicit way to disable the mysql_install_db codepath besides having a database already "configured" (ie, stuff in /var/lib/mysql/mysql)
# also, we set debconf keys to make APT a little quieter
RUN { \
        echo mysql-server mysql-server/data-dir select ''; \
        echo mysql-server mysql-server/root-pass password ''; \
        echo mysql-server mysql-server/re-root-pass password ''; \
        echo mysql-server mysql-server/remove-test-db select false; \
    } | debconf-set-selections \
    && apt-get update && apt-get install -y mysql-server && rm -rf /var/lib/apt/lists/* \
    && rm -rf /var/lib/mysql && mkdir -p /var/lib/mysql /var/run/mysqld \
    && chown -R mysql:mysql /var/lib/mysql /var/run/mysqld \
# ensure that /var/run/mysqld (used for socket and lock files) is writable regardless of the UID our mysqld instance ends up having at runtime
    && chmod 777 /var/run/mysqld

# comment out a few problematic configuration values
# don't reverse lookup hostnames, they are usually another container
RUN sed -Ei 's/^(bind-address|log)/#&/' /etc/mysql/my.cnf \
    && echo '[mysqld]\nskip-host-cache\nskip-name-resolve' > /etc/mysql/conf.d/docker.cnf

VOLUME /var/lib/mysql

COPY docker-entrypoint.sh /usr/local/bin/
RUN ln -s /usr/local/bin/docker-entrypoint.sh /entrypoint.sh # backwards compat
ENTRYPOINT ["docker-entrypoint.sh"]

EXPOSE 3306
CMD ["mysqld"]
