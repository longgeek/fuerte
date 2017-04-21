#!/bin/bash

docker network create --driver overlay --subnet 11.0.0.0/8 fuvism-learn
docker network create --driver overlay --subnet 12.0.0.0/8 fuvism-nginx
docker network create --driver overlay --subnet 13.0.0.0/8 fuvism-manager
