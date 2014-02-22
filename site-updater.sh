#!/bin/sh
cd $(dirname $0)
. ./etc/update.vars
[ -f ./etc/update.vars.custom ] && . ./etc/update.vars.custom

TMP=$(mktemp XXXXXXXXXX)
trap 'rm -f $TMP;exit' 0 1 2 15

$MTN pull -k "" "mtn://$MTNURL?$MTNBRANCH"
$MTN up 2>&1 | tee $TMP


if grep "^mtn: \(add\|patch\|dropp\|updat\)\(ed\|ing\) 'i2p2www/translations/" "$TMP" >/dev/null ; then
  echo "Translations updated, compiling messages"
  ./compile-messages.sh
fi

if grep "^mtn: updating 'i2p2www/.*\.py\|^mtn: updating 'i2p2www/.*/.*\.py" "$TMP" >/dev/null ; then
  echo "Python files changed, restarting server"
  touch $TOUCHFILE
fi
