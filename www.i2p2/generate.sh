#!/bin/sh
rm -rf out
mkdir out
cp -R static out/_static
python generate.py