#! /usr/bin/env bash
export devmode="--volume $(pwd):/var/www/i2p.www"
./site-updater-docker.sh runserver.sh