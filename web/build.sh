#!/bin/bash

set -euxo pipefail

export tag=`date +"%Y%m%d%H%M"`

docker build . -t registry.cn-heyuan.aliyuncs.com/methanal/scenespark-web:${tag}
docker push registry.cn-heyuan.aliyuncs.com/methanal/scenespark-web:${tag}

echo ${tag}
