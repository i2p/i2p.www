#! /usr/bin/env sh
virtualenv --distribute env
. env/bin/activate
#./setup_venv.sh
DEV=on ./runserver.py
