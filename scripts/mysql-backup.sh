#!/bin/bash


DATE=$(date "+%Y%m%d-%H%M%S")
docker exec -it fuvism-mysql \
    mysqldump -uroot \
              -p4jT3R4fEjQRz8n8s \
              allspark \
              > /opt/git/sql/allspark-$DATE.sql
SIZE=$(du -sh /opt/git/sql/allspark-$DATE.sql)
echo ""
echo "Done: $SIZE"
echo ""
