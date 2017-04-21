#!/bin/bash

USERS=$(ls /migrate/storage/user_data/)

for U in $USERS
do
    if [ -e /migrate/storage/user_data/$U/learn/online_course ]; then
        OLD_DATA_NUM=$(ls /migrate/storage/user_data/$U/learn/online_course | wc -l)
        DEVICE=$(rbd map ${U}"_learn")
        mount $DEVICE /mnt
        NEW_DATA_NUM=$(ls /mnt/online_course | wc -l)
        umount /mnt
        rbd unmap ${U}"_learn"
        if [ $OLD_DATA_NUM != $NEW_DATA_NUM ]; then
            echo $U
        fi
    fi
done
