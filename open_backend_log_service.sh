#!/bin/bash

set -euxo pipefail

export CONTAINER_ID=$(docker inspect --format="{{.Id}}" scenespark-dev-api-1)
export LOG_PATH=/var/lib/docker/containers/${CONTAINER_ID}/${CONTAINER_ID}-json.log
sudo chmod 666 ${LOG_PATH}

sudo docker rm -f backendlog
sudo docker run --name backendlog -p 0.0.0.0:11002:80 -v ${LOG_PATH}:/tmp/backend.log -v /home/luckybear/SceneSpark/pv-data/nginx/backendlog.dev.conf:/etc/nginx/conf.d/default.conf:ro --platform=linux/amd64 -d nginx
