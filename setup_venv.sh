#!/usr/bin/env bash
set -e
source ./project.vars

if [ ! -d $venv_dir ] ; then
    $venv --distribute $venv_dir
fi

source $venv_dir/bin/activate

pip install -r reqs.txt
