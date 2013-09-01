#!/bin/sh
. ./etc/translation.vars

if [ ! -e $POTDIR ]; then
    mkdir $POTDIR
fi

if [ $# -ge 1 ]
then
    TZ=UTC ./pybabel extract --msgid-bugs-address="http://trac.i2p2.de" \
                               --project=$PROJECT \
                               --version=$VERSION \
                               -F $BABELCFG/$1 \
                               -o $POTDIR/$1.pot $PROJDIR
else
    for domain in $(ls $BABELCFG); do
        if [ -e $POTDIR/$domain.pot ]; then
            mv $POTDIR/$domain.pot $POTDIR/$domain.pot.old
        fi
        TZ=UTC ./pybabel extract --msgid-bugs-address="http://trac.i2p2.de" \
                               --project=$PROJECT \
                               --version=$VERSION \
                               -F $BABELCFG/$domain \
                               -o $POTDIR/$domain.pot $PROJDIR
        diff -u $POTDIR/$domain.pot.old $POTDIR/$domain.pot | grep '^+' | grep -v '^+++' | grep -v '+"POT-Creation-Date' >/dev/null
        if [ $? -eq 1 ]; then
            mv $POTDIR/$domain.pot.old $POTDIR/$domain.pot
        fi
    done
fi
