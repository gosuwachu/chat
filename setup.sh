#!/bin/bash -ex

VENV_DIR=${VENV_DIR:-.venv}
if [ ! -d .venv ] ; then
    python3.11 -m venv "$VENV_DIR"
fi
source "$VENV_DIR/bin/activate"
pip3.11 install -r requirements.txt