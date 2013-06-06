#!/bin/sh
. ./translation.vars

TZ=UTC ./pybabel extract --msgid-bugs-address="http://trac.i2p2.de" \
                               --project=$PROJECT \
                               --version=$VERSION \
                               -F $BABELCFG \
                               -o $POTFILE $PROJDIR
