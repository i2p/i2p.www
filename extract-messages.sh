#!/bin/sh
. ./etc/translation.vars

export TZ=UTC

if [ ! -e $POTDIR ]; then
    mkdir $POTDIR
fi

# By setting the PYTHONPATH here we can help pybabel find 'our' highlighting
# extension and we can use any pybabel
export PYTHONPATH=i2p2www:$PYTHONPATH

if [ $# -ge 1 ]
then
    $PYBABEL extract --msgid-bugs-address="http://trac.i2p2.de" \
                               --project=$PROJECT \
                               --version=$VERSION \
                               -F $BABELCFG/$1 \
                               -o $POTDIR/$1.pot $PROJDIR
else
    for domain in $(ls $BABELCFG); do
        $PYBABEL extract --msgid-bugs-address="http://trac.i2p2.de" \
                               --project=$PROJECT \
                               --version=$VERSION \
                               -F $BABELCFG/$domain \
                               -o $POTDIR/$domain.pot $PROJDIR
    done
fi
