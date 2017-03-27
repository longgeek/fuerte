# Fuerte API Backend Project

## Getting Started

If you'd like to run from the master branch, you can clone the git repo:

    git clone git@git.pyindex.com:reviewdev/fuerte.git

## References

* http://wiki.pyindex.com

## How to use

1. INSTALL SUPERVISOR:

    apt-get install supervisor

2. INSTALL VIRTUALENV:

    apt-get install python-virtualenv

3. INSTALL PACKAGES:

    apt-get install python-dev redis-server

4. INSTALL FUERTE:

    cd /opt/git
    git clone git@git.pyindex.com:reviewdev/fuerte.git

5. CREATE VENV DIR:

    mkdir /storage
    cp -r /opt/git/fuerte/install/storage/venv /storage/

6. CREATE LOG DIR:

    mkdir /var/log/fuerte
    cp /opt/git/fuerte/install/etc/logrotate.d/fuerte /etc/logrotate.d/
    chown :adm /var/log/fuerte
    logrotate -f /etc/logrotate.d/fuerte
    service rsyslog restart

7. CONFIG FUERTE:

    mkdir /etc/fuerte
    cp /opt/git/fuerte/install/etc/fuerte/fuerte.conf.sample /etc/fuerte/fuerte.conf
    cp /opt/git/fuerte/install/etc/supervisor/conf.d/fuerte.conf.sample /etc/supervisor/conf.d/fuerte.conf

    vim /etc/fuerte/fuerte.conf
    # redis_pass YCTACMmimohBBiZRanibCnjJV8zdnwGs 设置 redis 访问密码

    vim /etc/redis/redis.conf
    55 行  bind 0.0.0.0 设置 redis 监听地址
    330 行 requirepass YCTACMmimohBBiZRanibCnjJV8zdnwGs 设置 redis 访问密码
    service redis-server restart

8. START SUPERVISOR SERVICE:

    service supervisor restart
    supervisorctl reread
    supervisorctl update
    supervisorctl start fuerte

9. LOG DETAIL:

    tail -f /var/log/fuerte/output.log
    tail -f /var/log/fuerte/errors.log
