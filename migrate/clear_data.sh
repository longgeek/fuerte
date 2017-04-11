#!/bin/bash


[ -e /migrate ] || echo "\nError: not found /migrate.\n"
[ -e /migrate ] || exit

rm -f $(find /migrate/storage/diff -name ".wh..wh.aufs")
rm -fr $(find /migrate/storage/diff -name ".wh..wh.orph")
rm -fr $(find /migrate/storage/diff -name ".wh..wh.plnk")

for i in `ls /migrate/storage/diff/`; 
do
    [ -e /migrate/storage/diff/$i/storage ] && rm -fr /migrate/storage/diff/$i/storage;
done
