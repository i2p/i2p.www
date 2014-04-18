#!/bin/sh
cat $1 | sed 's/..\:..\(\:..\)\?\s*//' | grep ^\< | sed 's/^<\([^>]*\)>.*/\1/' | sed 's/^[@+ ]//' | sort | uniq | grep -v iRelay
