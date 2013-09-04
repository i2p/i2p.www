#!/bin/sh
TMP=$(mktemp XXXXXXXXXX)
trap 'rm -f $TMP;exit' 0 1 2 15

mtn update 2>&1 | tee $TMP

if grep "^mtn: \(add\|dropp\|updat\)ing 'i2p2www/translations/" "$TMP" >/dev/null; then
  echo "Translations updated, compiling messages"
  ./compile-messages-i2hq.sh
fi

if grep "^mtn: updating 'i2p2www/.*\.py\|^mtn: updating 'i2p2www/.*/.*\.py" >/dev/null; then
  echo "Python files changed, restarting server"
  touch /tmp/2fcd2f17-c293-4f77-b4c9-9b266ba70daa
fi
