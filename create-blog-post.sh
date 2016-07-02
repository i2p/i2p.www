#!/bin/sh
BLOG_DIR="i2p2www/blog"

if [ $# -lt 3 ]
then
    echo "Usage: ./create-blog-post.sh name-in-url \"Title of blog post\" author [category]"
    exit
fi

name=$1
title=$2
author=$3
category=$4

date=`TZ=UTC date +%Y-%m-%d`
datedir=`TZ=UTC date  +%Y/%m/%d`
titleline=`printf '%*s' "$(expr length "$title")" | tr ' ' =`

post="$BLOG_DIR/$datedir/$name.draft.rst"

mkdir -p "$BLOG_DIR/$datedir"

cat >"$post" <<EOF
{% trans -%}
$titleline
$title
$titleline
{%- endtrans %}
.. meta::
    :author: $author
    :date: $date
EOF

if [ -n "$category" ]
then
cat >>"$post" <<EOF
    :category: $category
EOF
fi

cat >>"$post" <<EOF
    :excerpt: {% trans %}{% endtrans %}

{% trans -%}

{%- endtrans %}
EOF

echo "Draft blog post created: $post"
echo "See i2p2www/blog/README for more information."
