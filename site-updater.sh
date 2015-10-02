#!/bin/sh
cd $(dirname $0)
. ./etc/update.vars
[ -f ./etc/update.vars.custom ] && . ./etc/update.vars.custom

[ ! -f $TOUCHFILE ] && touch $TOUCHFILE

TMP=$(mktemp XXXXXXXXXX)
trap 'rm -f $TMP;exit' 0 1 2 15

$MTN pull -k "" "mtn://$MTNURL?$MTNBRANCH"
$MTN up 2>&1 | tee $TMP


if grep "^mtn: \(add\|patch\|dropp\|updat\)\(ed\|ing\) 'i2p2www/translations/" "$TMP" >/dev/null ; then
  echo "Translations updated, compiling messages"
  ./compile-messages.sh
fi

echo "Monotone revision: $(mtn log --no-files --no-graph --to h: | grep Revision | sed 's/Revision: //')" >./i2p2www/pages/include/mtnversion

if grep "^mtn: updating 'i2p2www/.*\.py\|^mtn: updating 'i2p2www/.*/.*\.py" "$TMP" >/dev/null ; then
  echo "Python files changed, restarting server"
  touch $TOUCHFILE
fi

[ -f ./.pybabel-stamp ] || ./compile-messages.sh
