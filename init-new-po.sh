#!/bin/sh
. ./etc/translation.vars

export TZ=UTC

if [ $# -ge 1 ]
then
    for domain in $(ls $BABELCFG); do
        $PYBABEL init -D $domain -i $POTDIR/$domain.pot -d $TRANSDIR -l $1
    done
else
    echo "Usage: ./init-new-po.sh lang"
fi
