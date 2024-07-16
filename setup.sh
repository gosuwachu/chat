#!/bin/bash -ex
if [ ! -d .venv ] ; then
    python3.11 -m venv .venv
fi
source .venv/bin/activate
pip3.11 install -r requirements.txt