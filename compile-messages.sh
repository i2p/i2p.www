#!/bin/sh
. ./translation.vars

if [ $# -ge 1 ]
then
    TZ=UTC env/bin/pybabel compile -D $1 -d $TRANSDIR
else
    for domain in $(ls $BABELCFG); do
        TZ=UTC env/bin/pybabel compile -D $domain -d $TRANSDIR
    done
fi
