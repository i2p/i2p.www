#!/bin/sh
. ./etc/translation.vars
export TZ=UTC

if [ $# -ge 1 ]
then
    $PYBABEL update -D $1 -i $POTDIR/$1.pot -d $TRANSDIR
    for file in $(ls i2p2www/translations/*/LC_MESSAGES/$1.po); do
        sed -i '/^#~/,+2d' $file
    done
else
    for domain in $(ls $BABELCFG); do
        $PYBABEL update -D $domain -i $POTDIR/$domain.pot -d $TRANSDIR
        for file in $(ls i2p2www/translations/*/LC_MESSAGES/$domain.po); do
            sed -i '/^#~/,+2d' $file
        done
    done
fi
