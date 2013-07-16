#!/bin/sh
. ./translation.vars

for domain in $(ls $BABELCFG); do
    TZ=UTC env/bin/pybabel update -D $domain -i $POTDIR/$domain.pot -d $TRANSDIR
done
