#! /usr/bin/env bash

## Set additional docker run arguments by changing the variable
## i2p_www_docker_run_args in an optional file called config.sh
## for example
##
##i2p_www_docker_run_args='-d'
## to run the site in the background, or
##
##i2p_www_docker_run_args='-t'
## to emulate a TTY

## To operate a quick and easy mirror of the I2P Site in a container
## simply clone the i2p.www source to a host with Docker installed, then 
## add:
##
##i2p_www_docker_run_args='-d'
## to config.sh
##
## Then add:
##
##*/10 * * * *	/path/to/i2p.www/site-updater-docker.sh
##
## to a crontab belonging to a member of the `docker` group. To add yourself
## to the `docker` group use the command:
##
##sudo adduser $(whoami) docker
##
## a more secure solution may be to create a user especially to run the
## docker crontab only, who is a member of the docker group. To do this,
##
##sudo adduser --disabled-password --disabled-login --ingroup docker docker
## however the specifics may vary from distribution to distribution.



if [ -f config.sh ]; then
	. config.sh
fi

if [ -z $port ]; then
	port="8090"
fi

if [ -z $i2p_www_branch ]; then
	i2p_www_branch=master
fi

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )" || exit
cd "$DIR" || exit

git pull origin $i2p_www_branch
docker build $i2p_www_docker_build_args -t i2p-mirror/mirror.i2p.www$suffix .
docker rm -f mirror.i2p.www$suffix
docker run $i2p_www_docker_run_args --name mirror.i2p.www$suffix -p 0.0.0.0:$port:80 i2p-mirror/i2p.www$suffix $@
