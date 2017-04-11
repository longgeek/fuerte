#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess

# 获取所有用户和对应的容器 ID 编号
p = subprocess.Popen(
    ["mysql -uMoVj45v1Z2wl3oNH -p \
            -h 172.16.0.232 telegraph_pole \
            -e 'select cid,name from apphome_container;' | \
            grep -v cid"],
    stdout=subprocess.PIPE,
    shell=True
)
data = p.stdout.readlines()
p.stdout.close()

# f = open("users.txt", "r")
# data = f.readlines()
# f.close()

users = []
new_data = []
for line in data:
    line = line.strip()
    cid = line.split("\t")[0]
    user = line.split("\t")[1].split("fuvism-default-")[-1]

    if user not in users:
        users.append(user)
        new_data.append("%s\t%s\n" % (cid, user))
    else:
        index = users.index(user)
        new_data[index] = "%s\t%s\n" % (cid, user)

print len(users)
print len(new_data)

fo = open("users.txt", "w")
fo.writelines(new_data)
fo.close()
