#!/bin/sh
. ./translation.vars

for domain in $(ls $BABELCFG); do
    TZ=UTC env/bin/pybabel compile -D $domain -d $TRANSDIR
done
