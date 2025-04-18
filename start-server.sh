#!/bin/bash
filepath=$(cd "$(dirname "$0")/"; pwd)
cd $filepath
poetry install --no-root
make server
