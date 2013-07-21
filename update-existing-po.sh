#!/bin/sh
. ./translation.vars

if [ $# -ge 1 ]
then
    TZ=UTC env/bin/pybabel update -D $1 -i $POTDIR/$1.pot -d $TRANSDIR
else
    for domain in $(ls $BABELCFG); do
        TZ=UTC env/bin/pybabel update -D $domain -i $POTDIR/$domain.pot -d $TRANSDIR
    done
fi
