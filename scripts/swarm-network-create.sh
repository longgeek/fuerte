#!/bin/bash

docker network create --driver overlay --subnet 11.0.0.0/8 fuvism-bases
docker network create --driver overlay --subnet 12.0.0.0/8 fuvism-nginx
