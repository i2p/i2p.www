#!/bin/sh

# This script is meant to be used on logs created by Limnoria's/Supybot's
# ChannelLogger plugin, but it may work with other IRC log formats.


LOGFILE="$1"
getmonth() {
    case ${1} in
        01)
            echo "January"
            ;;
        02)
            echo "February"
            ;;
        03)
            echo "March"
            ;;
        04)
            echo "April"
            ;;
        05)
            echo "May"
            ;;
        06)
            echo "June"
            ;;
        07)
            echo "July"
            ;;
        08)
            echo "August"
            ;;
        09)
            echo "September"
            ;;
        10)
            echo "October"
            ;;
        11)
            echo "November"
            ;;
        12)
            echo "December"
            ;;
        *)
            echo "Error"
            exit 1
    esac
}

error() {
    echo "Usage: $0 [logfile]"
    exit 1
}

print_rst() {
    HEADER="I2P dev meeting, $DATE @ 20:00 UTC"
    echo $HEADER
    LEN=$(expr length "${HEADER}")
    for I in $(seq $LEN); do printf '='; done
    printf '\n\nQuick recap\n-----------\n\n* **Present:**\n\n'
}

print_present(){
    # These regexes extract nicknames from current logs (created by Limnoria/Supybot) and the "historical" #i2p-dev logs
    sed -e '/^.*[0-9]\{2\}:[0-9]\{2\}:[0-9]\{2\}\s\+\*\*\*/d' \
        -e '/<.\+>/!d' \
        -e 's/.*<+fox>\s\+<\([^<>]\+\).*/\1/' \
        -e 's/^<\([^<>]\+\).*/\1,/' \
        -e 's/^\[[0-9]\{2\}:[0-9]\{2\}\(:[0-9]\{2\}\]\)\?\s\+<\([^<>]\+\)>.*/\2,/' \
        -e 's/^[0-9]\{2\}:[0-9]\{2\}\(:[0-9]\{2\}\)\?\s\+<\([^<>]\+\)>.*/\2,/' -e 's/^[@+ ]//g' "$LOGFILE"  \
        | grep -wv 'fox\|iRelay\|feed\|travis-ci\|jenkins\|RSS\|MTN\|BigBrother' | sort  | uniq
}

if [ ! -e $LOGFILE ]; then
    error
fi
set -- $(echo "$LOGFILE" |sed 's/^.\+i2p-dev\.\([0-9]\{4\}\)-\([0-9]\{2\}\)-\([0-9]\{2\}\).*/\1 \2 \3/')
MONTH=$(getmonth $2)
YEAR=$1
DAY=$3
DATE="${MONTH} ${DAY}, ${YEAR}"

# If the file passed to this script is named in the format *i2p-dev.YYYY-MM-DD*,
# this script will attempt to print a usable .rst file for the meeting.
# Otherwise just the "attendees" will be printed.

if [ $MONTH = 'Error' ]; then :; else
    print_rst
fi
print_present
