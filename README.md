# Fuerte API Backend Project

## Getting Started

If you'd like to run from the master branch, you can clone the git repo:

    git clone git@git.pyindex.com:reviewdev/fuerte.git

## References

* http://wiki.pyindex.com

## How to use

1. INSTALL SUPERVISOR:

    apt-get install supervisor

2. INSTALL PACKAGES:

    apt-get install python-dev python-rados python-tox libffi-dev libssl-dev libxml2-dev libxslt1-dev
    apt-get install redis-server

3. INSTALL FUERTE:

    mkdir /opt/git
    cd /opt/git
    git clone git@git.pyindex.com:reviewdev/fuerte.git
    cd fuerte/
    pip install -r requirements.txt

4. CREATE LOG DIR:

    mkdir /var/log/fuerte
    cp /opt/git/fuerte/install/etc/logrotate.d/fuerte /etc/logrotate.d/
    chown :adm /var/log/fuerte
    logrotate -f /etc/logrotate.d/fuerte
    service rsyslog restart

5. CONFIG FUERTE:

    mkdir /etc/fuerte
    cp /opt/git/fuerte/install/etc/fuerte/fuerte.conf.sample /etc/fuerte/fuerte.conf
    cp /opt/git/fuerte/install/etc/supervisor/conf.d/fuerte.conf.sample /etc/supervisor/conf.d/fuerte.conf

    vim /etc/fuerte/fuerte.conf
    # redis_pass YCTACMmimohBBiZRanibCnjJV8zdnwGs 设置 redis 访问密码

    vim /etc/redis/redis.conf
    55 行  bind 0.0.0.0 设置 redis 监听地址
    330 行 requirepass YCTACMmimohBBiZRanibCnjJV8zdnwGs 设置 redis 访问密码
    service redis-server restart

6. Sure Docker Host the "/storage/.system/.console/" exist.
   Use virtualenv build butterfly in the /storage/.system/.console/local/butterfly:

    mkdir -p /storage/.system
    pip install virtualenv
    virtualenv /storage/.system/.console
    source /storage/.system/.console/bin/activate
    cd /storage/.system/.console/local/
    git clone git@github.com:thstack/butterfly.git
    cd butterfly
    pip install -r requirements.txt
    python setup.py develop
    deactivate

7. Django database synchronization needs to enter the project directory,
   which adds a .bash directory, used to store a number of scripts.
   such as: switch directory

    mkdir /storage/.system/.bash/
    touch switchdir.sh
    #!/bin/bash

    export VIRTUAL_ENV=/storage/.system/.virtualenv/django/django-1.8.4
    export PATH=/storage/.system/.virtualenv/django/django-1.8.4/bin:$PATH
    [ -e $1 ] && cd $1
    bash


8. Sure Docker Host the "/storage/.virtualenv/" exist.
   The Django Practice topic is heavily dependent on it:

    # django-1.8.2
    mkdir -p /storage/.system/.virtualenv/django
    virtualenv /storage/.system/.virtualenv/django/django-1.8.2
    source /storage/.system/.virtualenv/django/django-1.8.2/bin/activate
    pip install "django==1.8.2"
    pip install ipdb
    deactivate
    sed -i "s/'django.middleware.clickjacking.XFrameOptionsMiddleware'/# 'django.middleware.clickjacking.XFrameOptionsMiddleware'/g" /storage/.system/.virtualenv/django/django-1.8.2/lib/python2.7/site-packages/django/conf/project_template/project_name/settings.py

    # django-1.8.4
    virtualenv /storage/.system/.virtualenv/django/django-1.8.4
    source /storage/.system/.virtualenv/django/django-1.8.4/bin/activate
    pip install "django==1.8.4"
    pip install ipdb
    deactivate
    sed -i "s/'django.middleware.clickjacking.XFrameOptionsMiddleware'/# 'django.middleware.clickjacking.XFrameOptionsMiddleware'/g" /storage/.system/.virtualenv/django/django-1.8.4/lib/python2.7/site-packages/django/conf/project_template/project_name/settings.py

9. Sure tree command the >= 1.7.0.
   Install:

    wget https://launchpadlibrarian.net/173977087/tree_1.7.0.orig.tar.gz
    tar zxvf tree_1.7.0.orig.tar.gz
    cd tree-1.7.0
    make
    make install

10. START SUPERVISOR SERVICE:

    service supervisor restart
    supervisorctl reread
    supervisorctl update
    supervisorctl start fuerte

11. LOG DETAIL:

    tail -f /var/log/fuerte/output.log
    tail -f /var/log/fuerte/errors.log
