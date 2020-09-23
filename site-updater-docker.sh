#! /usr/bin/env sh

git pull origin master
docker build -t i2p-mirror/i2p.www .
docker rm -f mirror.i2p.www
docker run -it --name mirror.i2p.www -p 0.0.0.0:8090:80 i2p-mirror/i2p.www
#docker run -td --name mirror.i2p.www --restart=always -p 0.0.0.0:5000:5000 i2p-mirror/i2p.www
