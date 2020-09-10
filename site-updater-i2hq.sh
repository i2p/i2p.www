#!/bin/sh
cd $(dirname $0)
. ./etc/update.vars
[ -f ./etc/update.vars.custom ] && . ./etc/update.vars.custom

[ ! -f $TOUCHFILE ] && touch $TOUCHFILE

TMP=$(mktemp XXXXXXXXXX)
trap 'rm -f $TMP;exit' 0 1 2 15

if [ -d ./.git ]; then
  git pull origin master | tee $TMP

  if grep "i2p2www/translations/" "$TMP" >/dev/null ; then
    echo "Translations updated, compiling messages"
    ./compile-messages-i2hq.sh
  fi

  echo "Git revision: $(git log -n 1 | grep commit | sed 's/commit //' | sed 's/ .*$//')" >./i2p2www/pages/include/mtnversion

  if grep "^git: updating 'i2p2www/.*\.py\|^mtn: updating 'i2p2www/.*/.*\.py" "$TMP" >/dev/null ; then
    echo "Python files changed, restarting server"
    touch $TOUCHFILE
  fi

else

  mtn pull "mtn://$MTNURL?$MTNBRANCH"
  mtn up 2>&1 | tee $TMP

  if grep "^mtn: \(add\|patch\|dropp\|updat\)\(ed\|ing\) 'i2p2www/translations/" "$TMP" >/dev/null ; then
    echo "Translations updated, compiling messages"
    ./compile-messages-i2hq.sh
  fi

  echo "Monotone revision: $(mtn log --no-files --no-graph --to h: | grep Revision | sed 's/Revision: //')" >./i2p2www/pages/include/mtnversion

  if grep "^mtn: updating 'i2p2www/.*\.py\|^mtn: updating 'i2p2www/.*/.*\.py" "$TMP" >/dev/null ; then
    echo "Python files changed, restarting server"
    touch $TOUCHFILE
  fi

fi

[ -f ./.pybabel-stamp ] || ./compile-messages.sh
