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
ENV NODE_PATH /opt/git/prerender/node_modules/


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
    apt-get -y install vim git wget curl dstat git-review python-dev python-pip supervisor \
                       libjpeg8-dev python-mysqldb openssh-server zlib1g-dev man-db libfontconfig1-dev && \
    curl -sL https://deb.nodesource.com/setup_4.x | sudo -E bash - && \
    apt-get -y install nodejs


#
# 设置 Vim 和 PIP
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
    wget https://raw.githubusercontent.com/chriskempson/tomorrow-theme/master/vim/colors/Tomorrow-Night.vim -P /etc/vim/colors/ && \
    mkdir /root/.pip && \
    echo "\n\
[global]\n\
index-url = http://pypi.douban.com/simple\n\
" > /root/.pip/pip.conf


#
# 克隆 Prerender 项目, 并安装
#
WORKDIR /opt/git
RUN git clone https://github.com/prerender/prerender && \
    cd /opt/git/prerender && \
    npm install -g cnpm --registry=https://registry.npm.taobao.org && \
    cnpm install forever && \
    cnpm install && \
    cnpm install prerender-access-log && \
    echo "\n\
[program:prerender]\n\
command=/opt/git/prerender/node_modules/forever/bin/forever -c 'node --harmony' --spinSleepTime 10000 -o /var/log/prerender/output.log -e /var/log/prerender/error.log /opt/git/prerender/server.js\n\
directory=/opt/git/prerender\n\
startsecs=0\n\
stopwaitsecs=0\n\
autostart=true\n\
autorestart=true\n\
stdout_logfile=/var/log/prerender/output.log\n\
stderr_logfile=/var/log/prerender/error.log\n\
" > /etc/supervisor/conf.d/prerender.conf

RUN echo "\n\
#!/usr/bin/env node\n\
var prerender = require('./lib');\n\
\n\
var server = prerender({\n\
    workers: process.env.PRERENDER_NUM_WORKERS,\n\
    iterations: process.env.PRERENDER_NUM_ITERATIONS,\n\
    accessLog: {\n\
        // Check out the file-stream-rotator docs for parameters\n\
        fileStreamRotator: {\n\
            filename: '/var/log/prerender/access-%DATE%.log',\n\
            frequency: 'daily',\n\
            date_format: 'YYYY-MM-DD',\n\
            verbose: false\n\
        },\n\
\n\
        // Check out the morgan docs for the available formats\n\
        morgan: {\n\
            format: 'combined'\n\
        }\n\
    }\n\
});\n\
\n\
\n\
server.use(prerender.sendPrerenderHeader());\n\
// server.use(prerender.basicAuth());\n\
// server.use(prerender.whitelist());\n\
server.use(prerender.blacklist());\n\
// server.use(prerender.logger());\n\
server.use(prerender.removeScriptTags());\n\
server.use(prerender.httpHeaders());\n\
// server.use(prerender.inMemoryHtmlCache());\n\
// server.use(prerender.s3HtmlCache());\n\
server.use(require('prerender-access-log'));\n\
\n\
server.start();\n\
" > /opt/git/prerender/server.js

#
# 配置项目
#
RUN mkdir /var/log/prerender

#
# 使用 supervisor 运行服务
#
CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/supervisord.conf"]
