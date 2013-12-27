#!/bin/sh
. ./etc/update.vars

TMP=$(mktemp XXXXXXXXXX)
trap 'rm -f $TMP;exit' 0 1 2 15

mtn pull "mtn://$MTNURL?$MTNBRANCH"
mtn up 2>&1 | tee $TMP


if grep "^mtn: \(add\|patch\|dropp\|updat\)\(ed\|ing\) 'i2p2www/translations/" "$TMP" >/dev/null ; then
  echo "Translations updated, compiling messages"
  ./compile-messages-i2hq.sh
fi

if grep "^mtn: updating 'i2p2www/.*\.py\|^mtn: updating 'i2p2www/.*/.*\.py" "$TMP" >/dev/null ; then
  echo "Python files changed, restarting server"
  touch $TOUCHFILE
fi
