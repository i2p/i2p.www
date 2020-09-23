#! /usr/bin/env sh

## Set additional docker run arguments by changing the variable
## i2p_www_docker_run_args

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )" || exit

git pull origin master
docker build -t i2p-mirror/i2p.www .
docker rm -f mirror.i2p.www
docker run -it $i2p_www_docker_run_args --name mirror.i2p.www -p 0.0.0.0:8090:80 i2p-mirror/i2p.www
#docker run -td --name mirror.i2p.www --restart=always -p 0.0.0.0:5000:5000 i2p-mirror/i2p.www
