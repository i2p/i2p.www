#!/bin/sh
. ./translation.vars

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
        TZ=UTC ./pybabel extract --msgid-bugs-address="http://trac.i2p2.de" \
                               --project=$PROJECT \
                               --version=$VERSION \
                               -F $BABELCFG/$domain \
                               -o $POTDIR/$domain.pot $PROJDIR
    done
fi
