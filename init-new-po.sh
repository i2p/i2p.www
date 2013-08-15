#!/bin/sh
. ./etc/translation.vars

if [ $# -ge 1 ]
then
    for domain in $(ls $BABELCFG); do
        TZ=UTC env/bin/pybabel init -D $domain -i $POTDIR/$domain.pot -d $TRANSDIR -l $1
    done
else
    echo "Usage: ./init-new-po.sh lang"
fi
