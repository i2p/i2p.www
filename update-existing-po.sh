#!/bin/sh
. ./babel/translation.vars

TZ=UTC env/bin/pybabel update -i $POTFILE -d $TRANSDIR
