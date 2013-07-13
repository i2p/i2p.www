#!/bin/sh
. ./babel/translation.vars

if [ $# -ge 1 ]
then
    TZ=UTC env/bin/pybabel init -i $POTFILE -d $TRANSDIR -l $1
else
    echo "Usage: ./init-new-po.sh lang"
fi
