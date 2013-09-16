#!/bin/sh
. ./etc/translation.vars

export TZ=UTC

if [ $# -ge 1 ]
then
    $PYBABEL compile -D $1 -d $TRANSDIR
else
    for domain in $(ls $BABELCFG); do
        $PYBABEL compile -D $domain -d $TRANSDIR
    done
fi
