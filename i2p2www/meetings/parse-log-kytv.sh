#!/bin/sh
sed -e 's/^[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}T//g' -e '/^[0-9]\{2\}:[0-9]\{2\}:[0-9]\{2\}\s\+\*\*\*/d' "${1}" > "${1}.nodate"
##
# The dumb parser will try to extract meetings from the following pattern:
# <nickname> 0. Hi            or <nickname> 0) Hi
# --meeting takes place---
# * nickname bafs the meeting closed
#
# If that format is not found we'll just strip off the date, modes, joins, etc., and advise that the
# log file is manually trimmed.
##
sed -n '/^[0-9]\{2\}:[0-9]\{2\}:[0-9]\{2\}\s\+<.\+>\s\+0[).].\+[Hh]i.*/,/^[0-9]\{2\}:[0-9]\{2\}:[0-9]\{2\}\s\+.*baf.\?s the meeting.*/p' < "${1}.nodate" > "${1}.out"

echo "========================================================================================================"
if [ ! -s ${1}.out ]; then
    echo "Please trim the file ${1}.out so that it contains the logs of the meeting."
    mv ${1}.nodate ${1}.out
    else
	    echo "The files ${1}.nodate and ${1}.out were created."
	    echo
	    printf "If lucky, ${1}.out just contains the logs of the meeting\nand requires little to no editing.\n\n"
	    printf "Otherwise, if this script made a mistake, you'll need to pare down ${1}.nodate.\n"
fi
echo "========================================================================================================"
