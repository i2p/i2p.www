#!/bin/sh
. ./translation.vars

TZ=UTC env/bin/pybabel extract --msgid-bugs-address="http://trac.i2p2.de" \
                               --project=$PROJECT \
                               --version=$VERSION \
                               -F $BABELCFG \
                               -o $POTFILE $PROJDIR
