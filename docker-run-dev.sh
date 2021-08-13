#! /usr/bin/env sh
virtualenv --distribute env
. env/bin/activate
./runserver.py
