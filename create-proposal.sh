#!/bin/sh
PROPOSAL_DIR="i2p2www/spec/proposals"

if [ $# -lt 4 ]
then
    echo "Usage: ./create-proposal.sh name-in-url \"Title of proposal\" author forum-url [file]"
    exit
fi

name=$1
title=$2
author=$3
thread=$4
file=$5

date=`date +%Y-%m-%d`
num=`expr $(expr substr $(ls -r "$PROPOSAL_DIR" | head -n1) 1 3) + 1`
titleline=`printf '%*s' "$(expr length "$title")" | tr ' ' =`

proposal="$PROPOSAL_DIR/$num-$name.rst"

cat >"$proposal" <<EOF
$titleline
$title
$titleline
.. meta::
    :author: $author
    :created: $date
    :thread: $thread
    :lastupdated: $date
    :status: Draft

.. contents::


Introduction
============

EOF

if [ -f "$file" ]
then
    cat "$file" >>"$proposal"
else
    echo >>"$proposal"
fi

echo "Proposal created: $proposal"
