#!/bin/sh
. ./etc/translation.vars
export TZ=UTC

if [ $# -ge 1 ]
then
    $PYBABEL update -D $1 -i $POTDIR/$1.pot -d $TRANSDIR
else
    for domain in $(ls $BABELCFG); do
        $PYBABEL update -D $domain -i $POTDIR/$domain.pot -d $TRANSDIR
    done
fi
