#!/bin/sh
TMP=tmp

mtn update 2>&1 | tee $TMP

cat $TMP | grep "^mtn: adding 'i2p2www/translations/\|^mtn: dropping 'i2p2www/translations/\|^mtn: updating 'i2p2www/translations/" >/dev/null
if [ $? -eq 0 ]; then
  echo "Translations updated, compiling messages"
  ./compile-messages-i2hq.sh
fi

cat $TMP | grep "^mtn: updating 'i2p2www/.*\.py\|^mtn: updating 'i2p2www/.*/.*\.py" >/dev/null
if [ $? -eq 0 ]; then
  echo "Python files changed, restarting server"
  touch /tmp/2fcd2f17-c293-4f77-b4c9-9b266ba70daa
fi

rm $TMP
