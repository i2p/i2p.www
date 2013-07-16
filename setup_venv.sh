#!/bin/sh
set -e
. ./project.vars

if [ ! $venv ]; then
    echo "ERROR: virtualenv not found!" >&2
else
    if [ ! -d $venv_dir ] ; then
        $venv --distribute $venv_dir
    fi

    . $venv_dir/bin/activate
    pip install -r reqs.txt
    # Apply multi-domain patch to Flask-Babel
    patch -p0 <multi-domain.patch
fi
